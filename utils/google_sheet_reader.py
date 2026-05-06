import requests

def fetch_channels_from_google_sheet(sheet_id, api_key):
    # Mengambil data dari tab 'api call' dalam range A1 hingga Z1000
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{sheet_id}/values/'api call'!A1:Z1000?key={api_key}"
    
    try:
        response = requests.get(url)
        data = response.json()
        rows = data.get("values", [])
    except Exception as e:
        print(f"❌ Error fetching Google Sheet: {e}")
        return []

    if not rows:
        print("⚠️ Tiada data dijumpai dalam Google Sheet.")
        return []

    # 1. Kenalpasti kedudukan (index) kolum berdasarkan header di baris pertama
    header = rows[0]
    try:
        name_idx = header.index("Name")
        link_idx = header.index("Link")
        sumber_idx = header.index("Sumber") 
    except ValueError as e:
        print(f"❌ Header Error: {e}. Pastikan kolum 'Name', 'Link', dan 'Sumber' wujud.")
        return []

    channel_data = []

    # 2. Fungsi bantuan untuk ambil data walaupun sel kosong/tak wujud dalam JSON
    def get_value(row_list, index, default=""):
        # Google API tidak hantar sel kosong di hujung baris, jadi kita check panjang list
        return row_list[index] if index < len(row_list) else default

    # 3. Proses setiap baris bermula dari baris kedua
    for row in rows[1:]:
        # Ambil link sebagai syarat utama
        channel_link = get_value(row, link_idx, "").strip()
        
        # Jika tiada link, kita skip baris tersebut
        if not channel_link:
            continue

        channel_data.append({
            "channel_name": get_value(row, name_idx, "Unknown"),
            "channel_link": channel_link,
            "sumber": get_value(row, sumber_idx, "") # Jika kosong, ia akan jadi ""
        })

    return channel_data
