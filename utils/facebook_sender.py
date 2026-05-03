import os
import json
import requests

FB_PAGE_ID = os.getenv("FB_PAGE_ID")
LONG_LIVED_USER_TOKEN = os.getenv("LONG_LIVED_USER_TOKEN")
HTTP_TIMEOUT = 60

_PAGE_TOKEN_CACHE = None

def get_fb_token():
    global _PAGE_TOKEN_CACHE
    if _PAGE_TOKEN_CACHE:
        return _PAGE_TOKEN_CACHE
    try:
        r = requests.get(
            "https://graph.facebook.com/me/accounts",
            params={"access_token": LONG_LIVED_USER_TOKEN},
            timeout=HTTP_TIMEOUT,
        )
        if r.ok:
            data = r.json().get("data", [])
            if data:
                _PAGE_TOKEN_CACHE = data[0]["access_token"]
                return _PAGE_TOKEN_CACHE
    except Exception as e:
        print(f"[FB Token Error] {e}")
    return None

def post_to_facebook(caption: str, image_paths: list = None, video_paths: list = None, sumber: str = None):
    token = get_fb_token()
    if not token:
        print("[FB] Error: No Page Token found.")
        return False

    # Tambah maklumat sumber di hujung caption jika ada
    full_caption = caption or ""
    if sumber:
        full_caption += f"\n\nSumber: {sumber}"

    try:
        # 1. Post Video (Priority)
        if video_paths and os.path.exists(video_paths[0]):
            with open(video_paths[0], "rb") as f:
                r = requests.post(
                    f"https://graph.facebook.com/{FB_PAGE_ID}/videos",
                    data={"description": full_caption, "access_token": token},
                    files={"source": f},
                    timeout=HTTP_TIMEOUT,
                )
            return r.ok

        # 2. Post Photos (Single or Multiple)
        elif image_paths:
            media_ids = []
            for path in image_paths:
                if not os.path.exists(path): continue
                with open(path, "rb") as f:
                    r = requests.post(
                        f"https://graph.facebook.com/{FB_PAGE_ID}/photos",
                        data={"published": "false", "access_token": token},
                        files={"source": f},
                        timeout=HTTP_TIMEOUT,
                    )
                if r.ok:
                    media_ids.append(r.json()["id"])

            if media_ids:
                payload = {"message": full_caption, "access_token": token}
                for i, mid in enumerate(media_ids):
                    payload[f"attached_media[{i}]"] = json.dumps({"media_fbid": mid})
                
                r = requests.post(f"https://graph.facebook.com/{FB_PAGE_ID}/feed", data=payload)
                return r.ok

        # 3. Post Text Only
        else:
            r = requests.post(
                f"https://graph.facebook.com/{FB_PAGE_ID}/feed",
                data={"message": full_caption, "access_token": token},
                timeout=HTTP_TIMEOUT,
            )
            return r.ok

    except Exception as e:
        print(f"[FB Post Error] {e}")
        return False
