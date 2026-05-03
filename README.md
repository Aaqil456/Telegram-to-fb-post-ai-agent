# 🤖 Telegram-to-FB Post AI Agent

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Telethon](https://img.shields.io/badge/Library-Telethon-orange.svg)
![Gemini](https://img.shields.io/badge/AI-Gemini_3.1_Flash-green.svg)

An intelligent automation agent designed to monitor Telegram channels, refine content using **Gemini AI**, and publish high-quality posts to a **Facebook Page**. This agent excels at handling complex media, specifically **Media Groups (Albums)**, ensuring they appear as a single cohesive post on Facebook.

---

## 🚀 Key Features

*   **Multi-Channel Monitoring**: Dynamically pulls target Telegram channels and source metadata from a central **Google Sheet**.
*   **Smart Media Grouping**: Automatically identifies Telegram albums (multiple photos) and bundles them into a **single Facebook post** instead of separate uploads.
*   **AI-Powered Localization**:
    *   Translates content into natural, conversational Malaysian Malay ("Ayat Kolokial Professional").
    *   **Strict Filtering**: Automatically purges external links, source tags (e.g., *Binance|TV*), and unwanted Call-to-Actions (CTAs).
*   **Duplicate Prevention**: Uses a local `results.json` database to track every successfully posted message ID.
*   **Versatile Media Support**: Handles Text-only, Single Images (.jpg), and Video files (.mp4).

---

## 📂 Project Architecture

| File | Responsibility |
| :--- | :--- |
| `main.py` | The central engine orchestrating the workflow from Telegram to Facebook. |
| `utils/telegram_reader.py` | Manages the Telethon client and the grouping logic for Media Groups/Albums. |
| `utils/facebook_sender.py` | Interacts with the Facebook Graph API to publish single/multi-photo and video posts. |
| `utils/ai_translator.py` | Refines and translates content using the Gemini 1.5 Flash model. |
| `utils/google_sheet_reader.py` | Fetches the target channel list and source metadata from Google Sheets. |
| `utils/json_writer.py` | Handles local persistence and deduplication of message IDs. |

---

## 🛠️ Prerequisites

*   **Python 3.10+**
*   **Telegram Credentials**: API ID and Hash from [my.telegram.org](https://my.telegram.org).
*   **Google Cloud Console**: Enabled Google Sheets API and an API Key.
*   **Facebook Graph API**: A Long-Lived User Token and Page ID.
*   **Gemini API Key**: Obtained from [Google AI Studio](https://aistudio.google.com).

---

## 📦 Installation & Setup

1. **Clone the Repository:**
   ```bash
   git clone [https://github.com/Aaqil456/Telegram-to-fb-post-ai-agent.git](https://github.com/Aaqil456/Telegram-to-fb-post-ai-agent.git)
   cd Telegram-to-fb-post-ai-agent
