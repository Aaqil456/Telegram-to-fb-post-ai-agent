import os
import asyncio
from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
from utils.google_sheet_reader import fetch_channels_from_google_sheet
from utils.telegram_reader import extract_channel_username, fetch_latest_messages
from utils.ai_translator import translate_text_gemini
from utils.facebook_sender import post_to_facebook
from utils.json_writer import save_results, load_posted_messages

async def main():
    telegram_api_id = int(os.environ['TELEGRAM_API_ID'])
    telegram_api_hash = os.environ['TELEGRAM_API_HASH']
    sheet_id = os.environ['GOOGLE_SHEET_ID']
    google_sheet_api_key = os.environ['GOOGLE_SHEET_API_KEY']

    posted_messages = load_posted_messages()
    result_output = []
    channels_data = fetch_channels_from_google_sheet(sheet_id, google_sheet_api_key)

    async with TelegramClient("telegram_session", telegram_api_id, telegram_api_hash) as client:
        for entry in channels_data:
            channel_username = extract_channel_username(entry["channel_link"])
            sumber_info = entry.get("sumber", "")
            
            # Fetch latest messages from Telegram
            messages = await fetch_latest_messages(telegram_api_id, telegram_api_hash, channel_username)

            for msg in messages:
                # De-duplication check
                if str(msg["id"]) in posted_messages:
                    continue

                # Translate content
                translated = translate_text_gemini(msg["text"])
                image_paths = []
                video_paths = []

                # Media Handling (Photos & Videos)
                if msg.get("photos") or msg.get("media"):
                    # Kita guna client sedia ada untuk download
                    if "photos" in msg: # Format dari telegram_reader anda
                        for i, photo_media in enumerate(msg["photos"]):
                            path = f"temp_photo_{msg['id']}_{i}.jpg"
                            await client.download_media(photo_media, path)
                            image_paths.append(path)
                    
                    # Tambahan logic untuk video jika ada
                    if hasattr(msg.get("original_msg"), 'media'):
                        orig = msg["original_msg"]
                        if isinstance(orig.media, MessageMediaDocument):
                            mime = getattr(orig.file, "mime_type", "")
                            if "video" in mime:
                                vpath = f"temp_video_{msg['id']}.mp4"
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
                    result_output.append({
                        "channel_link": entry["channel_link"],
                        "original_text": msg["text"],
                        "id": str(msg["id"]),
                        "date": str(msg["date"])
                    })

                # Cleanup temp files
                for p in image_paths + video_paths:
                    if os.path.exists(p): os.remove(p)

    if result_output:
        save_results(result_output)

if __name__ == "__main__":
    async asyncio.run(main())
