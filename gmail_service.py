import win32serviceutil
import win32service
import win32event
import servicemanager
import time
import os
import logging
import base64
import re
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

BASE_DIR = r"C:\gmail_mcp_bot"
CREDENTIALS_PATH = os.path.join(BASE_DIR, "credentials.json")
TOKEN_PATH = os.path.join(BASE_DIR, "token.json")
LOG_PATH = os.path.join(BASE_DIR, "service.log")


def authenticate():
    creds = None

    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)


def delete_spam(service):
    results = service.users().messages().list(
        userId='me',
        labelIds=['SPAM'],
        maxResults=10
    ).execute()

    messages = results.get('messages', [])

    for msg in messages:
        service.users().messages().trash(
            userId='me',
            id=msg['id']
        ).execute()

        logging.info(f"Spam deleted: {msg['id']}")


class GmailService(win32serviceutil.ServiceFramework):
    _svc_name_ = "GmailAutomationService"
    _svc_display_name_ = "Gmail Automation Background Service"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)

        logging.basicConfig(
            filename=LOG_PATH,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)

    def SvcDoRun(self):
        logging.info("Service started.")
        service = authenticate()

        while True:
            delete_spam(service)
            time.sleep(60)


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(GmailService)
