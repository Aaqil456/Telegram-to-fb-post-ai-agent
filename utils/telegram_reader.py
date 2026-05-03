import re

def extract_channel_username(url: str) -> str:
    if not url: return ""
    url = url.strip().rstrip('/')
    match = re.search(r'(?:t\.me/|@)([\w\d_]+)', url)
    return f"@{match.group(1)}" if match else url

async def fetch_latest_messages(client, channel_username):
    """
    Mengambil mesej tanpa menggunakan parameter 'group_by' langsung 
    untuk mengelakkan ralat Telethon.
    """
    messages_data = []
    media_groups = {}

    try:
        # Loop mesej secara normal. TIADA 'group_by' di sini.
        async for message in client.iter_messages(channel_username, limit=10):
            
            # Jika mesej sebahagian daripada album
            if message.grouped_id:
                if message.grouped_id not in media_groups:
                    media_groups[message.grouped_id] = {
                        "id": message.id,
                        "text": message.text or "",
                        "date": message.date,
                        "photos": [],
                        "original_msg": message
                    }
                
                if message.media:
                    media_groups[message.grouped_id]["photos"].append(message.media)
                
                # Pastikan caption diambil daripada mesej yang ada teks dalam album tu
                if message.text and not media_groups[message.grouped_id]["text"]:
                    media_groups[message.grouped_id]["text"] = message.text
            
            # Jika mesej tunggal
            else:
                if message.text or message.media:
                    messages_data.append({
                        "id": message.id,
                        "text": message.text or "",
                        "date": message.date,
                        "photos": [message.media] if message.media else [],
                        "original_msg": message
                    })

        # Masukkan balik media groups ke dalam list utama
        for g_id in media_groups:
            messages_data.append(media_groups[g_id])

    except Exception as e:
        print(f"⚠️ Error fetching from {channel_username}: {e}")
        
    # Sort ikut ID supaya post tak terbalik
    return sorted(messages_data, key=lambda x: x["id"])
