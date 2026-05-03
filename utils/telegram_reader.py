import re

def extract_channel_username(url: str) -> str:
    """
    Ekstrak username daripada URL Telegram (contoh: t.me/username atau @username).
    """
    if not url:
        return ""
    url = url.strip().rstrip('/')
    # Mencari pattern username selepas t.me/ atau jika user letak @ terus
    match = re.search(r'(?:t\.me/|@)([\w\d_]+)', url)
    if match:
        return f"@{match.group(1)}"
    return url

async def fetch_latest_messages(client, channel_username):
    """
    Mengambil mesej menggunakan client yang di-pass dari main.py.
    Dibuat ringkas supaya tidak mengganggu sesi SQLite.
    """
    messages = []
    try:
        # Mengambil 5 mesej terbaru dari channel
        async for message in client.iter_messages(channel_username, limit=1):
            # Kita kumpul data penting untuk diproses oleh main.py
            messages.append({
                "id": message.id,
                "text": message.text or "",
                "date": message.date,
                # Simpan media untuk pengesanan gambar/video di main.py
                "photos": [message.media] if hasattr(message, 'media') and message.media else [],
                "original_msg": message
            })
    except Exception as e:
        print(f"⚠️ Error fetching from {channel_username}: {e}")
        
    return messages
