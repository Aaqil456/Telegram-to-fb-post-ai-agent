import os
import asyncio
import time
from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
from utils.google_sheet_reader import fetch_channels_from_google_sheet
from utils.telegram_reader import extract_channel_username, fetch_latest_messages
from utils.ai_translator import translate_text_gemini
from utils.facebook_sender import post_to_facebook
from utils.json_writer import save_results, load_posted_messages

async def main():
    # Load Environment Variables
    telegram_api_id = int(os.environ.get('TELEGRAM_API_ID', 0))
    telegram_api_hash = os.environ.get('TELEGRAM_API_HASH', '')
    sheet_id = os.environ.get('GOOGLE_SHEET_ID', '')
    google_sheet_api_key = os.environ.get('GOOGLE_SHEET_API_KEY', '')

    if not all([telegram_api_id, telegram_api_hash, sheet_id, google_sheet_api_key]):
        print("❌ Missing essential environment variables. Please check your GitHub Secrets.")
        return

    # Load previously posted IDs to avoid duplicates
    posted_messages = load_posted_messages()
    result_output = []
    
    # Fetch channel list from Google Sheet
    channels_data = fetch_channels_from_google_sheet(sheet_id, google_sheet_api_key)

    # Start Telegram Client
    async with TelegramClient("telegram_session", telegram_api_id, telegram_api_hash) as client:
        for entry in channels_data:
            channel_link = entry.get("channel_link", "")
            if not channel_link:
                continue
                
            channel_username = extract_channel_username(channel_link)
            sumber_info = entry.get("sumber", "")
            
            print(f"🔍 Checking channel: {channel_username}")
            
            # Fetch latest messages from Telegram
            messages = await fetch_latest_messages(telegram_api_id, telegram_api_hash, channel_username)

            for msg in messages:
                msg_id = str(msg["id"])
                
                # Check if already posted
                if msg_id in posted_messages:
                    continue

                print(f"🚀 Processing message ID: {msg_id}")

                # Translate content
                translated = translate_text_gemini(msg["text"])
                image_paths = []
                video_paths = []

                # Media Handling
                # 1. Check for photos from telegram_reader format
                if msg.get("photos"):
                    for i, photo_media in enumerate(msg["photos"]):
                        path = f"temp_photo_{msg_id}_{i}.jpg"
                        await client.download_media(photo_media, path)
                        image_paths.append(path)
                
                # 2. Check for videos from original message
                if msg.get("original_msg"):
                    orig = msg["original_msg"]
                    if hasattr(orig, 'media') and isinstance(orig.media, MessageMediaDocument):
                        mime = getattr(orig.file, "mime_type", "")
                        if "video" in mime:
                            vpath = f"temp_video_{msg_id}.mp4"
                            await client.download_media(orig.media, vpath)
                            video_paths.append(vpath)

                # Post to Facebook
                success = post_to_facebook(
                    caption=translated,
                    image_paths=image_paths,
                    video_paths=video_paths,
                    sumber=sumber_info
                )

                if success:
                    print(f"✅ Successfully posted to Facebook: {msg_id}")
                    result_output.append({
                        "channel_link": channel_link,
                        "original_text": msg["text"],
                        "id": msg_id,
                        "date": str(msg["date"]),
                        "status": "Posted to FB"
                    })
                    # Add to memory to prevent re-posting in same run
                    posted_messages.append(msg_id)
                else:
                    print(f"❌ Failed to post message {msg_id} to Facebook.")

                # Cleanup temp files
                for p in image_paths + video_paths:
                    if os.path.exists(p):
                        try:
                            os.remove(p)
                        except Exception as e:
                            print(f"⚠️ Failed to delete temp file {p}: {e}")
                
                # Small delay to avoid hitting FB API rate limits
                time.sleep(2)

    # Save all new successful posts to results.json
    if result_output:
        save_results(result_output)
        print(f"💾 Saved {len(result_output)} new entries to results.json")

if __name__ == "__main__":
    # Fixed syntax here
    asyncio.run(main())
