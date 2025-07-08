import os.path
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
CREDS_FILE = "credentials.json"
TOKEN_FILE = "token.json"


def get_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)


def fetch_from_label(service, label):
    results = service.users().messages().list(userId="me", labelIds=[label]).execute()
    messages = results.get("messages", [])
    output = ""
    for m in messages:
        msg = (
            service.users()
            .messages()
            .get(userId="me", id=m["id"], format="raw")
            .execute()
        )
        data = base64.urlsafe_b64decode(msg["raw"].encode("ASCII")).decode(
            "utf-8", errors="ignore"
        )
        output += data + "\n\n"
    return output


def list_labels(service):
    results = service.users().labels().list(userId="me").execute()
    labels = results.get("labels", [])

    print("Available labels:")
    for label in labels:
        print(f"Name: {label['name']}, ID: {label['id']}")


if __name__ == "__main__":
    svc = get_service()
    list_labels(svc)
    text = fetch_from_label(
        svc, "Label_2552442229938484180"
    )  # o 'NEWSLETTERAI' se user label
    with open("newsletter_gapi.txt", "w", encoding="utf-8") as f:
        f.write(text)
    print("Finish! File: newsletter_gapi.txt")
