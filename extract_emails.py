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
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
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


def list_and_choose_label(service):
    results = service.users().labels().list(userId="me").execute()
    labels = results.get("labels", [])

    if not labels:
        print("No label available!")
        return None

    print("\n📋 Available labels:")
    print("-" * 50)
    for i, label in enumerate(labels, 1):
        print(f"{i:2d}. {label['name']}")

    print("-" * 50)

    while True:
        try:
            choice = input(
                f"\nChoose a Label (1-{len(labels)}) or 'q' to exit: "
            ).strip()

            if choice.lower() in ["q", "quit", "exit"]:
                print("Operation cancelled.")
                return None

            choice_num = int(choice)
            if 1 <= choice_num <= len(labels):
                selected_label = labels[choice_num - 1]
                print(
                    f"\n✅ Selected: {selected_label['name']} (ID: {selected_label['id']})"
                )
                return selected_label["id"]
            else:
                print(f"❌ Enter a number between 1 and {len(labels)}")

        except ValueError:
            print("❌ Enter a valid number")
        except KeyboardInterrupt:
            print("\n\nOperation cancelled.")
            return None


if __name__ == "__main__":
    svc = get_service()

    # Permetti all'utente di scegliere la label
    selected_label_id = list_and_choose_label(svc)

    if selected_label_id:
        print(f"\n🔄 Retrieving e-mails from the selected label...")
        text = fetch_from_label(svc, selected_label_id)

        with open("newsletter_gapi.txt", "w", encoding="utf-8") as f:
            f.write(text)

        print("✅ Finished! File: newsletter_gapi.txt")
    else:
        print("❌ No label selected. Programme terminated.")
