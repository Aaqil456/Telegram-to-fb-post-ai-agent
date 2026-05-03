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
    # 1. Load Environment Variables dari GitHub Secrets
    telegram_api_id = int(os.environ.get('TELEGRAM_API_ID', 0))
    telegram_api_hash = os.environ.get('TELEGRAM_API_HASH', '')
    sheet_id = os.environ.get('GOOGLE_SHEET_ID', '')
    google_sheet_api_key = os.environ.get('GOOGLE_SHEET_API_KEY', '')

    if not all([telegram_api_id, telegram_api_hash, sheet_id, google_sheet_api_key]):
        print("❌ Missing essential environment variables. Check GitHub Secrets.")
        return

    # 2. Muat turun ID lama untuk elak post berulang
    posted_messages = load_posted_messages()
    result_output = []
    
    # 3. Ambil senarai channel dari Google Sheet
    channels_data = fetch_channels_from_google_sheet(sheet_id, google_sheet_api_key)

    # 4. Buka sesi Telegram (Hanya SATU sesi dibuka untuk elak 'database is locked')
    async with TelegramClient("telegram_session", telegram_api_id, telegram_api_hash) as client:
        for entry in channels_data:
            channel_link = entry.get("channel_link", "")
            if not channel_link:
                continue
                
            channel_username = extract_channel_username(channel_link)
            sumber_info = entry.get("sumber", "")
            
            print(f"🔍 Checking channel: {channel_username}")
            
            # 5. Ambil mesej terbaru (termasuk logik kumpul album/Media Group)
            messages = await fetch_latest_messages(client, channel_username)

            for msg in messages:
                msg_id = str(msg["id"])
                
                # Semak duplication
                if msg_id in posted_messages:
                    continue

                print(f"🚀 Processing message ID: {msg_id}")

                # 6. Terjemah teks menggunakan Gemini
                translated = translate_text_gemini(msg["text"])
                image_paths = []
                video_paths = []

                # 7. Kendalikan Media (Gambar & Video)
                # Download semua gambar dalam album
                if msg.get("photos"):
                    for i, photo_media in enumerate(msg["photos"]):
                        if photo_media:
                            # Index 'i' digunakan supaya nama fail unik bagi setiap gambar dalam album
                            path = f"temp_photo_{msg_id}_{i}.jpg"
                            await client.download_media(photo_media, path)
                            if os.path.exists(path):
                                image_paths.append(path)
                
                # Download video (jika ada)
                if msg.get("original_msg"):
                    orig = msg["original_msg"]
                    if hasattr(orig, 'media') and isinstance(orig.media, MessageMediaDocument):
                        mime = getattr(orig.file, "mime_type", "")
                        if "video" in mime:
                            vpath = f"temp_video_{msg_id}.mp4"
                            await client.download_media(orig.media, vpath)
                            if os.path.exists(vpath):
                                video_paths.append(vpath)

                # 8. Post ke Facebook sebagai satu post (Album/Video/Text)
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
                    posted_messages.append(msg_id)
                else:
                    print(f"❌ Failed to post message {msg_id}.")

                # 9. Cuci fail sementara (Cleanup)
                for p in image_paths + video_paths:
                    if os.path.exists(p):
                        try:
                            os.remove(p)
                        except:
                            pass
                
                # Delay sikit untuk hormati API rate limit
                time.sleep(2)

    # 10. Simpan rekod hantaran baru ke results.json
    if result_output:
        save_results(result_output)
        print(f"💾 Saved {len(result_output)} new entries to results.json")

if __name__ == "__main__":
    # Menjalankan fungsi main menggunakan asyncio
    asyncio.run(main())
