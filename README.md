# 📬 Gmail Label Email Extractor (Python + Gmail API)

A Python script to extract all emails under a specific Gmail label and save their content as readable text. It uses the official Gmail API with OAuth2 authentication.

**Great for:**
* Feeding newsletters to LLMs or AI tools
* Archiving and summarizing Gmail messages
* Building personal data sets from your inbox

⚠️ **credentials.json** is not included in this repository for security reasons.


## 🚀 Getting Started: Enable Gmail API on Google Cloud

1. Go to https://console.cloud.google.com/
2. At the top, click "Select project" → "New project"
3. Name your project (e.g. GmailExtract) → Create

### 🔐 Enable Gmail API:

1. Visit: https://console.cloud.google.com/apis/library/gmail.googleapis.com
2. Click "Enable"

### 🧾 Create OAuth2 credentials:

1. Go to: https://console.cloud.google.com/apis/credentials
2. Click "+ CREATE CREDENTIALS" → "OAuth client ID"
3. If prompted, configure the consent screen:
   * App name: Gmail Extractor
   * Support email: your own
   * Save
4. Continue creating credentials:
   * Application type: Desktop app
   * Name: Gmail Extractor Python
   * Click CREATE
5. Download the **credentials.json** file
6. Move it to the root of the project (DO NOT commit it to GitHub)

### 👥 Add Test Users (Important!):

Since your app is in development mode, you need to add your email as a test user:

1. Go to: https://console.cloud.google.com/apis/credentials/consent
2. Under "Test users", click "+ ADD USERS"
3. Add your Gmail address (the one you want to extract emails from)
4. Click "SAVE"

⚠️ **Without this step, you'll get authentication errors when trying to access your Gmail!**

## 📦 Installation

Install the required Python packages:

```bash
pip install -r requirements.txt
```

**requirements.txt:**
```
google-api-python-client
google-auth-httplib2
google-auth-oauthlib
```

## 🛠️ Usage

1. Run the Python script:

```bash
python extract_emails.py
```

2. On first run, a browser window will open asking you to log in and authorize access to your Gmail account.

3. The script will display a list of available Gmail labels:

```
📋 Label disponibili:
--------------------------------------------------
 1. CHAT
 2. SENT
 3. INBOX
 4. IMPORTANT
 5. TRASH
 6. DRAFT
 ..
 14. STARRED
 15. UNREAD
 16. Unwanted
 .. Other Custom Labels you've created
--------------------------------------------------
```

4. Choose a label by entering its number (e.g., type `4` for Important)

5. Select the output format:

```
📄 Formato di output:
--------------------------------------------------
1. 🔤 Formato semplificato (leggibile, solo contenuto importante)
2. 📋 Formato raw completo (tutto il contenuto email originale)
--------------------------------------------------

Scegli formato (1-2): 
```

6. The script will extract all emails from the selected label and save them to:
   - **newsletter_simple.txt** (for simplified format)
   - **newsletter_raw.txt** (for raw format)

### 📊 Output Formats

#### 🔤 Simplified Format (Recommended)
Clean, readable format with only essential information:

```
================================================================================
📧 EMAIL #1
================================================================================
📅 Data: Wed, 08 Jan 2025 10:30:00 +0100
👤 Da: newsletter@example.com
👥 A: your.email@gmail.com
📝 Oggetto: Weekly Newsletter - Important Updates
================================================================================

This is the clean email content without HTML tags, headers, or technical data.
Perfect for feeding to LLMs or reading/analyzing email content.

All formatting is preserved but simplified for better readability.

================================================================================
FINE EMAIL #1
================================================================================
```

#### 📋 Raw Format
Complete email data including all headers, encoding, and technical information. Useful for technical analysis or debugging.

### 💡 Tips:
- You can type `q` to cancel the operation
- **Simplified format is recommended** for most use cases (AI analysis, reading, etc.)
- **Raw format is useful** for technical analysis or debugging


## 🔒 Security Notes

* Never commit `credentials.json` or `token.json` to version control 
* Keep your OAuth2 credentials secure and private


