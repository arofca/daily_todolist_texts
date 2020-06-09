from twilio.rest import Client
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import date

def text(request):

    # In this setup, security variables live in the same file as the SA key in SECRETS.json
    KEYS = json.load(open('SECRETS.json'))
    account_sid = KEYS['account_sid']
    auth_token = KEYS['auth_token']
    phone_number = KEYS['phone_number']
    messaging_service_sid = KEYS['messaging_service_sid']
    sheet_key = KEYS['sheet_key']

    # Data Extraction
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
             'SECRETS.json', scope)    gc = gspread.authorize(credentials)

    wks = gc.open_by_key(sheet_key)
    sheet = wks.worksheet("Today's To-Do")
    data = sheet.get("B2:E")
    headers = data.pop(0)
    df = pd.DataFrame(data, columns=headers)
    day = date.today().strftime('%Y-%m-%d')
    todays = df[(df['Date Due'] <= day)
                & (df['Status'] != 'Completed')][['Task']]

    # Formatting the Message Body
    tasks = len(todays.index)
    if tasks > 1:
        body = '''
Today's Big Deliverables:
'''
    elif tasks == 1:
        body = '''
Today's Big Deliverable:
'''
    else:
        body = "Nothing Due Today! Check the Taskmaster for Things Due Later!"

    for i in todays['Task']:
        body = body + " -" + i + '''
'''
    #Send the Text!
    client = Client(account_sid, auth_token)
    message = client.messages \
        .create(
             body=body,
             messaging_service_sid=messaging_service_sid,
             to=phone_number
         )
    print('Message Sent')