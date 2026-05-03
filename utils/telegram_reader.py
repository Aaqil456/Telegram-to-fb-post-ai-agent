import re

def extract_channel_username(url: str) -> str:
    if not url: return ""
    url = url.strip().rstrip('/')
    match = re.search(r'(?:t\.me/|@)([\w\d_]+)', url)
    return f"@{match.group(1)}" if match else url

async def fetch_latest_messages(client, channel_username):
    """
    Mengambil mesej dan menguruskan grouping (album) dengan betul.
    """
    messages_data = []
    processed_groups = set() 

    try:
        # 1. Gunakan iter_messages secara normal tanpa 'group_by'
        async for message in client.iter_messages(channel_username, limit=10):
            
            # 2. Jika mesej adalah sebahagian daripada album
            if message.grouped_id:
                if message.grouped_id in processed_groups:
                    continue
                
                # 3. BARU GUNAKAN get_messages di sini untuk kumpul album
                # Parameter 'group_by' diletakkan di sini, bukan di iter_messages
                album_messages = await client.get_messages(
                    channel_username, 
                    ids=message.id, 
                    group_by=message.grouped_id
                )
                
                caption = ""
                all_media = []
                for m in album_messages:
                    if m.text: 
                        caption = m.text
                    if m.media: 
                        all_media.append(m.media)
                
                messages_data.append({
                    "id": message.id,
                    "text": caption,
                    "date": message.date,
                    "photos": all_media, 
                    "original_msg": message
                })
                processed_groups.add(message.grouped_id)

            # 4. Jika mesej tunggal
            else:
                if message.text or message.media:
                    messages_data.append({
                        "id": message.id,
                        "text": message.text or "",
                        "date": message.date,
                        "photos": [message.media] if message.media else [],
                        "original_msg": message
                    })
                    
    except Exception as e:
        print(f"⚠️ Error fetching from {channel_username}: {e}")
        
    return messages_data
