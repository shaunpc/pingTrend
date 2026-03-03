# PingTrend - COLLECT-SQLITE.PY
#   to record results from PING command
#   both min/max/ave for each minute,
#   and the error types/rates
#   and STORES in local SQLITE database

import datetime
import sys
from database import Database
from do_ping import batch_ping
import logging

# Configuration
PING_HOST = 'www.google.com'
DEBUG = False  # Set to True for verbose output
# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = r"C:\Users\shaun\PycharmProjects\pingTrend\pingdatabase.sqlite"
RANGE_DATA = "PINGDATA"
RANGE_ERRORS = "PINGERROR"
# The table creation statements
sql_create_data_table = '''CREATE TABLE IF NOT EXISTS pingdata (
         ping_timestamp datetime,
         ping_target text,
         response_min integer, 
         response_ave integer, 
         response_max integer, 
         error_count integer 
         )'''
sql_create_error_table = '''CREATE TABLE IF NOT EXISTS pingerror (
         ping_timestamp datetime,
         ping_target text,
         err_type text,
         err_full text 
         )'''

# Setup logging
logging.basicConfig(level=logging.DEBUG if DEBUG else logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def store_data(sheetrange, data):
    result = ''
    for data_row in data:
        if sheetrange == RANGE_ERRORS:
            sql_insert = '''INSERT INTO pingerror (ping_timestamp, ping_target, err_type, err_full)
                        VALUES (?,?,?,?)'''
            sql_values = (data_row[0], data_row[1], data_row[2], data_row[3])
        else:
            sql_insert = '''INSERT INTO pingdata (ping_timestamp, ping_target, response_min, response_ave, 
                    response_max, error_count) VALUES (?,?,?,?,?,?)'''
            # (timestamp, ping_target, counter.min(), counter.ave(), counter.max(), counter_err.count())
            sql_values = (data_row[0], data_row[1], data_row[2], data_row[3], data_row[4], data_row[5])
        try:
            result = db.insert(sql_insert, sql_values)
        except Exception as e:
            logger.error(f"ERROR variable:data: {data}")
            logger.error(f"ERROR exception: {e}")
            logger.error(f"RESULT : {result}")
            return data
        else:
            logger.debug(f"ALL GOOD : Inserted {result} rows")
            return []


# Main Routine.
if __name__ == '__main__':

    # PREP THE DATA STORE = SQLITE
    db = Database(SPREADSHEET_ID)

    # if "CLEAN" is passed as param, then reset the data collected
    if 'clean' in sys.argv:
        logger.info("CLEAN: Dropping existing data and tables")
        db.execute('''DROP TABLE pingdata''')
        db.execute('''DROP TABLE pingerror''')

    logger.info("CREATE: Creating data collection tables if necessary")
    db.execute(sql_create_data_table)
    db.execute(sql_create_error_table)

    logger.info("CHECK: Checking table structures")
    logger.info(db.select("select sql from sqlite_master where name = 'pingdata'"))
    logger.info(db.select("select sql from sqlite_master where name = 'pingerror'"))

    # START THE COMMON PROCESS
    logger.info(f"Running {__file__}")
    logger.info("Starting batch data collection at {}".format(datetime.datetime.now()))
    unsaved_data = []
    unsaved_errors = []

    while True:
        # grab a minutes worth of PING data
        cnt_ping, cnt_err, err_details = batch_ping(PING_HOST)

        if cnt_err > 0:
            logger.warning(f"Unsaved errors (START): {unsaved_errors}")
            # err_details is already a list-of-lists, so just add to anything unsaved
            unsaved_errors += err_details
            logger.warning(f"Unsaved errors (POST-APP): {unsaved_errors}")
            unsaved_errors = store_data(RANGE_ERRORS, unsaved_errors)
            logger.warning(f"Unsaved errors (AFTER): {unsaved_errors}")

        # add the summary list to anything unsaved
        unsaved_data.append([cnt_ping.start.__str__(), PING_HOST, cnt_ping.min(), cnt_ping.ave(), cnt_ping.max(),
                             cnt_err, cnt_ping.start.strftime('%A')])
        unsaved_data = store_data(RANGE_DATA, unsaved_data)
