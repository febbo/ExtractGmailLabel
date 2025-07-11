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


def fetch_from_label(service, label, format_type="raw"):
    results = service.users().messages().list(userId="me", labelIds=[label]).execute()
    messages = results.get("messages", [])
    output = ""

    print(f"📧 Found {len(messages)} emails to be processed...")

    for i, m in enumerate(messages, 1):
        print(f"⏳ Processing emails {i}/{len(messages)}...", end="\r")

        if format_type == "simple":
            # Formato semplificato e leggibile
            msg = (
                service.users()
                .messages()
                .get(userId="me", id=m["id"], format="full")
                .execute()
            )

            # Estrai informazioni chiave
            payload = msg.get("payload", {})
            headers = payload.get("headers", [])

            # Funzione per trovare header specifici
            def get_header(name):
                for header in headers:
                    if header["name"].lower() == name.lower():
                        return header["value"]
                return "N/A"

            subject = get_header("subject")
            from_email = get_header("from")
            date = get_header("date")
            to_email = get_header("to")

            # Estrai il contenuto del messaggio
            def extract_body(part):
                body = ""
                if "parts" in part:
                    for subpart in part["parts"]:
                        body += extract_body(subpart)
                elif part.get("mimeType") == "text/plain":
                    data = part.get("body", {}).get("data", "")
                    if data:
                        body += base64.urlsafe_b64decode(data).decode(
                            "utf-8", errors="ignore"
                        )
                elif part.get("mimeType") == "text/html":
                    # Se non c'è testo plain, usa HTML ma pulito
                    data = part.get("body", {}).get("data", "")
                    if data:
                        html_content = base64.urlsafe_b64decode(data).decode(
                            "utf-8", errors="ignore"
                        )
                        # Rimuovi tag HTML base (puoi migliorare questo)
                        import re

                        clean_text = re.sub(r"<[^>]+>", "", html_content)
                        clean_text = re.sub(r"\s+", " ", clean_text).strip()
                        body += clean_text
                return body

            body = extract_body(payload).strip()

            # Formatta l'output in modo leggibile
            output += f"""{"=" * 80}
📧 EMAIL #{i}
{"=" * 80}
📅 Date: {date}
👤 From: {from_email}
👥 To: {to_email}
📝 Subject: {subject}
{"=" * 80}

{body}

{"=" * 80}
END EMAIL #{i}
{"=" * 80}

"""

        else:
            # Formato raw originale
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

    print(f"✅ Process {len(messages)} emails!")
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


def choose_format():
    print("\n📄 Output format:")
    print("-" * 50)
    print("1. 🔤 Simplified format (readable, only important content)")
    print("2. 📋 Full raw format (all original email content)")
    print("-" * 50)

    while True:
        try:
            choice = input("Choose format (1-2): ").strip()

            if choice.lower() in ["q", "quit", "exit"]:
                return None

            if choice == "1":
                print("✅ Selected: Simplified format")
                return "simple"
            elif choice == "2":
                print("✅ Selected: Full raw format")
                return "raw"
            else:
                print("❌ Enter 1 or 2")

        except KeyboardInterrupt:
            print("\n\nOperation cancelled.")
            return None


if __name__ == "__main__":
    svc = get_service()

    # Permetti all'utente di scegliere la label
    selected_label_id = list_and_choose_label(svc)

    if selected_label_id:
        format_type = choose_format()

        if format_type:
            print(f"\n🔄 Retrieving e-mails from the selected label...")
            text = fetch_from_label(svc, selected_label_id, format_type)

            # Nome file diverso in base al formato
            filename = (
                f"newsletter_{'simple' if format_type == 'simple' else 'raw'}.txt"
            )

            with open(filename, "w", encoding="utf-8") as f:
                f.write(text)

            print(f"✅ Finished! File: {filename}")
        else:
            print("❌ No format selected. Programme terminated.")
    else:
        print("❌ No label selected. Programme terminated.")
