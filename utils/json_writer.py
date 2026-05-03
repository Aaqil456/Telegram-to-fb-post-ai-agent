import json
import os
from datetime import datetime

def save_results(messages, file_path="results.json"):
    """
    Simpan mesej baru ke dalam results.json.
    Menguruskan format simpanan secara konsisten dalam bentuk dictionary.
    """
    existing_messages = []

    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}

        if isinstance(data, dict):
            existing_messages = data.get("messages", [])
        elif isinstance(data, list):
            existing_messages = data

    # Gabungkan mesej sedia ada dengan mesej baru
    combined_messages = existing_messages + messages

    # Simpan semula dengan timestamp terkini
    data = {
        "timestamp": datetime.now().isoformat(),
        "messages": combined_messages
    }
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def load_posted_messages(file_path="results.json"):
    """
    Memuatkan semua ID mesej yang telah berjaya dipost ke Facebook
    untuk mengelakkan duplication.
    """
    if not os.path.exists(file_path):
        return []

    with open(file_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return []

    if isinstance(data, dict):
        items = data.get("messages", [])
    elif isinstance(data, list):
        items = data
    else:
        items = []

    # Ambil ID unik mesej Telegram
    posted_ids = []
    for msg in items:
        if isinstance(msg, dict):
            if "id" in msg:
                posted_ids.append(str(msg["id"]))
            elif "telegram_id" in msg:
                posted_ids.append(str(msg["telegram_id"]))

    return posted_ids
