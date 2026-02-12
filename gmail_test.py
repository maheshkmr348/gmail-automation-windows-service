import base64
from email.mime.text import MIMEText
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly'
]
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

creds = None

# Check if token.json exists
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)

# If no valid credentials available, login again
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)

    # Save the credentials for next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())


service = build('gmail', 'v1', credentials=creds)

message = MIMEText("Second test message from automation system!")
message['to'] = "maheshkmr3489@gmail.com"
message['subject'] = "Gmail MCP Test"

raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

service.users().messages().send(
    userId="me",
    body={'raw': raw}
).execute()

print("\n📩 Reading Unread Emails...\n")

results = service.users().messages().list(
    userId='me',
    labelIds=['UNREAD'],
    maxResults=5
).execute()

messages = results.get('messages', [])

if not messages:
    print("No unread messages found.")
else:
    for msg in messages:
        msg_data = service.users().messages().get(
            userId='me',
            id=msg['id']
        ).execute()

        headers = msg_data['payload']['headers']

        subject = next(
            (header['value'] for header in headers if header['name'] == 'Subject'),
            "No Subject"
        )

        sender = next(
            (header['value'] for header in headers if header['name'] == 'From'),
            "Unknown Sender"
        )

        print("\n📩 Reading Unread Emails...\n")

results = service.users().messages().list(
    userId='me',
    labelIds=['UNREAD'],
    maxResults=5
).execute()

messages = results.get('messages', [])

if not messages:
    print("No unread messages found.")
else:
    for msg in messages:
        msg_data = service.users().messages().get(
            userId='me',
            id=msg['id'],
            format='full'
        ).execute()

        headers = msg_data['payload']['headers']

        subject = next(
            (header['value'] for header in headers if header['name'] == 'Subject'),
            "No Subject"
        )

        sender = next(
            (header['value'] for header in headers if header['name'] == 'From'),
            "Unknown Sender"
        )

        print("From:", sender)
print("Subject:", subject)

# Extract body
parts = msg_data['payload'].get('parts', [])
body = ""

if parts:
    for part in parts:
        if part['mimeType'] == 'text/plain':
            data = part['body']['data']
            body = base64.urlsafe_b64decode(data).decode('utf-8')
            break
else:
    data = msg_data['payload']['body'].get('data')
    if data:
        body = base64.urlsafe_b64decode(data).decode('utf-8')

# 👇 ADD THIS
import re
body = re.sub(r'\n\s*\n', '\n\n', body)
body = body.strip()

print("\n📄 Clean Email Body:\n")
print(body[:1000])
print("=" * 70)

