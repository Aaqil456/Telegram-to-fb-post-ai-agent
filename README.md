This is the professional README.md for your project, written in English. It covers the technical architecture, setup process, and core features of your AI agent.

🤖 Telegram-to-FB Post AI Agent
This AI Agent is designed to automate the process of gathering information from multiple Telegram channels, translating and refining the content using Gemini AI, and publishing the results to a Facebook Page automatically. It features advanced handling for media albums (Media Groups) to ensure content looks professional and native on Facebook.

🚀 Key Features
Multi-Channel Monitoring: Dynamically reads a list of Telegram channels and sources from a Google Sheet.

Smart Media Grouping: Automatically detects Telegram albums (multiple photos) and groups them into a single Facebook post instead of separate uploads.

AI-Powered Translation: Translates content into natural, conversational Malaysian Malay while purging external links, source tags (e.g., Binance|TV), and unwanted calls-to-action.

Duplicate Prevention: Tracks posted messages via a results.json database to ensure no content is ever posted twice.

Full Media Support: Handles text-only posts, single images (.jpg), and video files (.mp4).

📂 Project Structure
main.py: The central workflow engine that orchestrates the data flow from Telegram to Facebook.

utils/telegram_reader.py: Manages the Telethon client and the logic for grouping album messages.

utils/facebook_sender.py: Interacts with the Facebook Graph API to publish single/multi-photo and video posts.

utils/ai_translator.py: Handles content refinement using the Gemini 1.5 Flash model.

utils/google_sheet_reader.py: Fetches the target channel list and source metadata from Google Sheets.

utils/json_writer.py: Manages the local persistence of posted message IDs.

🛠️ Prerequisites
Python 3.10+

Telegram API Credentials: API ID and Hash from my.telegram.org.

Google Cloud Console: Enabled Google Sheets API and an API Key.

Facebook Graph API: A Long-Lived User Token and Page ID with pages_manage_posts and pages_read_engagement permissions.

Gemini API Key: From Google AI Studio.

📦 Installation & Setup
Clone the Repository:

Bash
git clone https://github.com/Aaqil456/Telegram-to-fb-post-ai-agent.git
cd Telegram-to-fb-post-ai-agent


2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
Configure Environment Variables:
Create a .env file or set these in your GitHub Secrets:

TELEGRAM_API_ID

TELEGRAM_API_HASH

GOOGLE_SHEET_ID

GOOGLE_SHEET_API_KEY

FB_PAGE_ID

LONG_LIVED_USER_TOKEN

GEMINI_API_KEY

⚙️ How It Works
Extract: The script fetches a list of Telegram channels from the designated Google Sheet.

Read: The telegram_reader scans for the latest messages. If it detects a grouped_id, it aggregates all associated media into a single object.

Process: Content is sent to Gemini AI to be translated into a "colloquial yet professional" Malay tone.

Publish: Media is downloaded temporarily, uploaded to the Facebook Graph API, and then purged from the local environment to save space.

⚠️ Important Notes
Concurrency: This system uses a single shared TelegramClient session to avoid sqlite3.OperationalError: database is locked errors.

Rate Limiting: Includes built-in delays (time.sleep) to respect the API quotas of both Google and Facebook.
