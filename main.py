from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import schedule
import requests
import time

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# number of NCOs
K_NCO = 1
# webhook urls
WH_URLS = ["https://hooks.slack.com/workflows/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",
           "",
           "",
           ""]

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '1bxOTACcm_LZ-iHJmF4ES5X-TfuzQMkMeJg2PsPNraRs'
RANGE_NAME = 'sheet1!C2:C' + str(K_NCO + 1)


def main():
    # schedule.every().friday.at('19:00').do(check)
    # schedule.every().saturday.at('19:00').do(check)
    # schedule.every().sunday.at('10:00').do(check)
    # schedule.every().sunday.at('19:00').do(check)
    schedule.every().monday.do(reset)

    schedule.every().monday.at('14:00').do(check)

    while True:
        schedule.run_pending()
        time.sleep(1)


def get_sheet():
    creds = None

    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    return service.spreadsheets()


def reset():
    print('resetting...')

    sheet = get_sheet()
    values = [[]]
    for k in range(K_NCO):
        values[0].append(0)

    body = {
        'range': RANGE_NAME,
        'majorDimension': 'COLUMNS',
        'values': values
    }
    sheet.values().update(
        spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME,
        valueInputOption='RAW', body=body).execute()


def check():
    print('checking...')
    sheet = get_sheet()

    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range=RANGE_NAME).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        # Code here
        for k in range(K_NCO):
            if '0' == (values[k][0]):
                requests.post(WH_URLS[k])


if __name__ == '__main__':
    main()