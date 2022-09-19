import pickle
import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


def get_google_creds(scopes):
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    # Sometimes, an "Invalid Grant: Token has been expired or revoked" message comes up...
    # Simply, delete TOKEN.PICKLE, and restart -- it will request Google Account sign-in to recreate.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                # IF THIS FAILS - and we will need to delete TOKEN.PICKLE and try again...
                # ERROR
                # C:\Users\shaun\PycharmProjects\pingTrend > Traceback(most recent call last):
                # File "C:\Users\shaun\PycharmProjects\pingTrend\collect-sheets.py", line  50, in < module >
                #     creds = get_google_creds(SCOPES)
                # File "C:\Users\shaun\PycharmProjects\pingTrend\get_google_creds.py", line 21, in get_google_creds
                #     creds.refresh(Request())
                # File "C:\Users\shaun\AppData\Roaming\Python\Python39\site-packages\google\oauth2\credentials.py",
                #   line 200, in refresh access_token, refresh_token, expiry, grant_response = _client.refresh_grant(
                # File "C:\Users\shaun\AppData\Roaming\Python\Python39\site-packages\google\oauth2\_client.py",
                #   line 248, in refresh_grant response_data = _token_endpoint_request(request, token_uri, body)
                # File "C:\Users\shaun\AppData\Roaming\Python\Python39\site-packages\google\oauth2\_client.py",
                #   line 124, in _token_endpoint_request _handle_error_response(response_body)
                # File "C:\Users\shaun\AppData\Roaming\Python\Python39\site-packages\google\oauth2\_client.py",
                #   line 60, in _handle_error_response raise exceptions.RefreshError(error_details, response_body)
                # google.auth.exceptions.RefreshError: ('invalid_grant: Token has been expired or revoked.',
                #      '{\n  "error": "invalid_grant",\n  "error_description": "Token has been expired or revoked."\n}')
            except Exception as ex:
                print("CREDS REFRESH ERROR: ", ex.__str__())
                print("Trying to delete token.pickle")
                os.remove("token.pickle")
                print("Done, trying to refresh Creds again")
                creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', scopes)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds
