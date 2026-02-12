import os
import time
import base64
import re
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']


# ---------------- AUTHENTICATION ---------------- #

def authenticate():
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)


# ---------------- READ FULL UNREAD EMAILS ---------------- #

def read_unread(service):
    print("\n📥 Checking Unread Emails...\n")

    results = service.users().messages().list(
        userId='me',
        labelIds=['UNREAD'],
        maxResults=5
    ).execute()

    messages = results.get('messages', [])

    if not messages:
        print("No unread emails found.")
        return

    for msg in messages:
        msg_data = service.users().messages().get(
            userId='me',
            id=msg['id'],
            format='full'
        ).execute()

        headers = msg_data['payload']['headers']

        subject = next(
            (h['value'] for h in headers if h['name'] == 'Subject'),
            "No Subject"
        )

        sender = next(
            (h['value'] for h in headers if h['name'] == 'From'),
            "Unknown Sender"
        )

        # Extract body
        body = ""
        parts = msg_data['payload'].get('parts')

        if parts:
            for part in parts:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data')
                    if data:
                        body = base64.urlsafe_b64decode(data).decode('utf-8')
                        break
        else:
            data = msg_data['payload']['body'].get('data')
            if data:
                body = base64.urlsafe_b64decode(data).decode('utf-8')

        body = re.sub(r'\n\s*\n', '\n\n', body).strip()

        print("📩 UNREAD EMAIL")
        print("From   :", sender)
        print("Subject:", subject)
        print("Body:\n", body[:1000])
        print("=" * 80)


# ---------------- DELETE SPAM ---------------- #

def delete_spam(service):
    print("\n🗑 Checking Spam Folder...\n")

    results = service.users().messages().list(
        userId='me',
        labelIds=['SPAM'],
        maxResults=20
    ).execute()

    messages = results.get('messages', [])

    if not messages:
        print("No spam emails found.")
        return

    for msg in messages:
        msg_data = service.users().messages().get(
            userId='me',
            id=msg['id'],
            format='metadata',
            metadataHeaders=['Subject', 'From']
        ).execute()

        headers = msg_data['payload']['headers']

        subject = next(
            (h['value'] for h in headers if h['name'] == 'Subject'),
            "No Subject"
        )

        sender = next(
            (h['value'] for h in headers if h['name'] == 'From'),
            "Unknown Sender"
        )

        print("Deleting SPAM:")
        print("From   :", sender)
        print("Subject:", subject)
        print("-" * 60)

        service.users().messages().trash(
            userId='me',
            id=msg['id']
        ).execute()


# ---------------- DELETE PROMOTIONS ---------------- #

def delete_promotions(service):
    print("\n🛍 Checking Promotions Folder...\n")

    results = service.users().messages().list(
        userId='me',
        labelIds=['CATEGORY_PROMOTIONS'],
        maxResults=20
    ).execute()

    messages = results.get('messages', [])

    if not messages:
        print("No promotion emails found.")
        return

    for msg in messages:
        msg_data = service.users().messages().get(
            userId='me',
            id=msg['id'],
            format='metadata',
            metadataHeaders=['Subject', 'From']
        ).execute()

        headers = msg_data['payload']['headers']

        subject = next(
            (h['value'] for h in headers if h['name'] == 'Subject'),
            "No Subject"
        )

        sender = next(
            (h['value'] for h in headers if h['name'] == 'From'),
            "Unknown Sender"
        )

        print("Deleting PROMOTION:")
        print("From   :", sender)
        print("Subject:", subject)
        print("-" * 60)

        service.users().messages().trash(
            userId='me',
            id=msg['id']
        ).execute()


# ---------------- MAIN LOOP ---------------- #

if __name__ == "__main__":
    service = authenticate()

    print("🚀 Gmail Full Monitor Started...")
    print("Press CTRL + C to stop.\n")

    while True:
        read_unread(service)
        delete_spam(service)
        delete_promotions(service)
        time.sleep(60)
