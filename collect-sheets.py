# PingTrend - COLLECT-SHEETS.PY
#   to record results from PING command
#   both min/max/ave for each minute,
#   and the error types/rates
#   and STORES in Google-Sheets on Google-Drive
#   Enables my AppSheet tool picks it up automatically...
#   https://www.appsheet.com/start/2aa910a9-b1bd-44e2-9caf-835da802c1bf#appName=UntitledApp-1995485

import datetime

import googleapiclient
import googleapiclient.errors
from googleapiclient.discovery import build
from get_google_creds import get_google_creds
from do_ping import batch_ping

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '1msPTg36_M0BGCJTqKDcixZYpDTUx1ohBhZrcK09_8mE'        # MyDrive\pingtrend
RANGE_DATA = 'PingData!A1:F1'
RANGE_ERRORS = 'PingErrors!A1:D1'
PING_HOST = 'www.google.com'


def store_data(sheetrange, data):
    body = {"majorDimension": "ROWS", "values": data}
    result = ''
    try:
        result = sheet.values().append(
            spreadsheetId=SPREADSHEET_ID,
            includeValuesInResponse=False,
            range=sheetrange,
            body=body,
            valueInputOption="USER_ENTERED"
        ).execute()
    except Exception as e:
        print("ERROR variable:data: {}".format(data))
        print("ERROR exception: {}".format(e))
        print("RESULT : ".format(result))
        return data
    else:
        # print("ALL GOOD : {} ROWS : {}".format(result['updates']['updatedRows'], result))
        return []


# Main Routine.
if __name__ == '__main__':

    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    creds = get_google_creds(SCOPES)

    # Set up the Sheets API
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()

    print("Starting batch data collection at {}".format(datetime.datetime.now()))
    unsaved_data = []
    unsaved_errors = []

    while True:
        # grab a minutes worth of PING data
        cnt_ping, cnt_err, err_details = batch_ping(PING_HOST)

        if cnt_err > 0:
            print("Unsaved errors (START): {}".format(unsaved_errors))
            # err_details is already a list-of-lists, so just add to anything unsaved
            unsaved_errors += err_details
            print("Unsaved errors (POST-APP): {}".format(unsaved_errors))
            unsaved_errors = store_data(RANGE_ERRORS, unsaved_errors)
            print("Unsaved errors (AFTER): {}".format(unsaved_errors))
            # if len(unsaved_data) > 0:
            #     print("Warning UNSAVED ERROR DATA : {}".format(len(unsaved_data)))

        # add the summary list to anything unsaved
        unsaved_data.append([cnt_ping.start, PING_HOST, cnt_ping.min(), cnt_ping.ave(), cnt_ping.max(), cnt_err])
        unsaved_data = store_data(RANGE_DATA, unsaved_data)
        # if len(unsaved_data) > 0:
        #     print("Warning UNSAVED PING DATA : {}".format(len(unsaved_data)))
