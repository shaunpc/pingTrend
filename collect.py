# PingTrend - COLLECT.PY
#   to record results from PING command
#   both min/max/ave for each minute,
#   and the error types/rates

import subprocess
import datetime
import sys
import time
from database import Database
from counter import Counter

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
         response_error text 
         )'''
sql_insert_data = '''INSERT INTO pingdata (ping_timestamp, ping_target, response_min, response_ave, 
        response_max, error_count) VALUES (?,?,?,?,?,?)'''
sql_insert_error = '''INSERT INTO pingerror (ping_timestamp, ping_target, response_error)
            VALUES (?,?,?)'''


# Executes a PING on the passed address, and returns either response time or the error message returned
def ping(host):
    error = None
    time = -1
    exec_ping = subprocess.run(["ping", "-n", "1" "-4", host], capture_output=True)
    if exec_ping.returncode == 0:
        lines = exec_ping.stdout.splitlines()
        if lines[2][:10] == b'Reply from':
            time = lines[2].split()[4][5:-2].decode('utf-8')
        else:
            error = lines[2]
    else:
        error = exec_ping.stdout
    return float(time), error


# Main Routine.
if __name__ == '__main__':
    db = Database(r"C:\Users\shaun\PycharmProjects\pingTrend\pingdatabase.sqlite")

    # if "CLEAN" is passed as param, then reset the data collected
    if 'clean' in sys.argv:
        print("Performing data cleansing")
        db.execute('''DROP TABLE pingdata''')
        db.execute('''DROP TABLE pingerror''')

    print("Prepping data collection tables")
    db.execute(sql_create_data_table)
    db.execute(sql_create_error_table)

    ping_target = "www.google.com"

    # Start the counters
    counter = Counter("DATA")
    counter_err = Counter("ERROR")
    timestamp = datetime.datetime.now()
    last_min = timestamp.minute

    print("Starting data collection at {}".format(timestamp))
    try:
        while True:
            time.sleep(0.25)
            timestamp = datetime.datetime.now()
            this_min = timestamp.minute
            rt, err = ping(ping_target)
            if err:
                db.insert(sql_insert_error, (timestamp, ping_target, err))
                counter_err.add(1)
            else:
                counter.add(rt)

            # Store the min/ave/max/error data each minute
            if this_min != last_min:
                values = (timestamp, ping_target, counter.min(), counter.ave(), counter.max(), counter_err.count())
                print(values)
                db.insert(sql_insert_data, values)
                last_min = this_min
                counter.reset()
                counter_err.reset()
    except KeyboardInterrupt:
        print("Finishing data collection at {}".format(timestamp))
        counter.show()
        counter_err.show()
        db.insert(sql_insert_data, (timestamp, ping_target, counter.min(), counter.ave(), counter.max(), counter_err.count()))
        db.close()
