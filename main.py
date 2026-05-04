import os
import asyncio
import time
from telethon import TelegramClient
from telethon.tl.types import MessageMediaDocument
from utils.google_sheet_reader import fetch_channels_from_google_sheet
from utils.telegram_reader import extract_channel_username, fetch_latest_messages
from utils.ai_translator import translate_text_gemini
from utils.facebook_sender import post_to_facebook
from utils.json_writer import save_results, load_posted_messages

async def main():
    # 1. Load Environment Variables
    telegram_api_id = int(os.environ.get('TELEGRAM_API_ID', 0))
    telegram_api_hash = os.environ.get('TELEGRAM_API_HASH', '')
    sheet_id = os.environ.get('GOOGLE_SHEET_ID', '')
    google_sheet_api_key = os.environ.get('GOOGLE_SHEET_API_KEY', '')

    if not all([telegram_api_id, telegram_api_hash, sheet_id, google_sheet_api_key]):
        print("❌ Missing essential environment variables. Check GitHub Secrets.")
        return

    # 2. Muat ID lama untuk deduplication
    posted_messages = load_posted_messages()
    result_output = []
    
    # 3. Ambil senarai channel dari Google Sheet
    channels_data = fetch_channels_from_google_sheet(sheet_id, google_sheet_api_key)

    # 4. Buka SATU sesi Telegram
    # Pastikan nama session "telegram_session" selari dengan .session file kau
    async with TelegramClient("telegram_session", telegram_api_id, telegram_api_hash) as client:
        for entry in channels_data:
            channel_link = entry.get("channel_link", "")
            if not channel_link:
                continue
                
            channel_username = extract_channel_username(channel_link)
            sumber_info = entry.get("sumber", "")
            
            print(f"🔍 Checking channel: {channel_username}")
            
            # 5. Ambil mesej terbaru
            messages = await fetch_latest_messages(client, channel_username)

            for msg in messages:
                msg_id = str(msg["id"])
                
                # Check if already posted
                if msg_id in posted_messages:
                    continue

                print(f"🚀 Processing message ID: {msg_id}")

                # 6. Terjemah teks guna Gemini
                original_text = msg.get("text", "")
                translated = translate_text_gemini(original_text)
                
                # --- LANGKAH 6.5: SEMAKAN TERJEMAHAN ---
                # Jika mesej ada teks, tapi hasil translate sama dengan asal 
                # (Maksudnya Gemini error & return fallback), kita SKIP post ini.
                if original_text.strip() != "" and translated == original_text:
                    print(f"⚠️ Skipping post {msg_id} sebab Gemini gagal translate (Fallback detected).")
                    continue
                # ---------------------------------------

                image_paths = []
                video_paths = []

                # 7. Kendalikan Media (Download)
                if msg.get("photos"):
                    for i, photo_media in enumerate(msg["photos"]):
                        if photo_media:
                            path = f"temp_photo_{msg_id}_{i}.jpg"
                            await client.download_media(photo_media, path)
                            if os.path.exists(path):
                                image_paths.append(path)
                
                # Pengesanan Video
                if msg.get("original_msg"):
                    orig = msg["original_msg"]
                    if hasattr(orig, 'media') and isinstance(orig.media, MessageMediaDocument):
                        mime = getattr(orig.file, "mime_type", "")
                        if "video" in mime:
                            vpath = f"temp_video_{msg_id}.mp4"
                            await client.download_media(orig.media, vpath)
                            if os.path.exists(vpath):
                                video_paths.append(vpath)

                # 8. Post ke Facebook
                # translated akan hantar teks BM jika berjaya, atau skip jika gagal
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
                        "original_text": original_text,
                        "id": msg_id,
                        "date": str(msg["date"]),
                        "status": "Posted to FB"
                    })
                    posted_messages.append(msg_id)
                else:
                    print(f"❌ Failed to post message {msg_id} to Facebook.")

                # 9. Cleanup fail sementara
                for p in image_paths + video_paths:
                    if os.path.exists(p):
                        try:
                            os.remove(p)
                        except:
                            pass
                
                # Delay sikit antara posts
                await asyncio.sleep(2)

    # 10. Simpan rekod larian
    if result_output:
        save_results(result_output)
        print(f"💾 Saved {len(result_output)} new entries to results.json")

if __name__ == "__main__":
    asyncio.run(main())
