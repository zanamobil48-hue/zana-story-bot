import os
import json
from pyrogram import Client
from PIL import Image, ImageFilter

API_ID = int(os.environ.get("TELEGRAM_API_ID"))
API_HASH = os.environ.get("TELEGRAM_API_HASH")
SESSION_STRING = os.environ.get("TELEGRAM_SESSION_STRING")
CHANNEL_USERNAME = os.environ.get("TELEGRAM_CHANNEL", "Zanamobile1")

STATE_FILE = "last_message.json"
STORY_SIZE = (1080, 1920)


def load_last_id():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            data = json.load(f)
            return data.get("last_id", 0)
    return 0


def save_last_id(message_id: int):
    with open(STATE_FILE, "w") as f:
        json.dump({"last_id": message_id}, f)


def fit_to_story(input_path: str, output_path: str):
    img = Image.open(input_path).convert("RGB")
    target_w, target_h = STORY_SIZE

    bg = img.copy()
    bg_ratio = max(target_w / bg.width, target_h / bg.height)
    bg = bg.resize((int(bg.width * bg_ratio) + 1, int(bg.height * bg_ratio) + 1))
    bg = bg.crop((
        (bg.width - target_w) // 2,
        (bg.height - target_h) // 2,
        (bg.width - target_w) // 2 + target_w,
        (bg.height - target_h) // 2 + target_h,
    ))
    bg = bg.filter(ImageFilter.GaussianBlur(40))

    fg_ratio = min(target_w / img.width, target_h / img.height)
    new_size = (int(img.width * fg_ratio), int(img.height * fg_ratio))
    fg = img.resize(new_size)

    offset = ((target_w - fg.width) // 2, (target_h - fg.height) // 2)
    bg.paste(fg, offset)

    bg.save(output_path, quality=95)


def main():
    app = Client(
        "zana_story_bot",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=SESSION_STRING,
    )

    with app:
        last_id = load_last_id()
        messages = list(app.get_chat_history(CHANNEL_USERNAME, limit=5))

        if not messages:
            print("هیچ پۆستێک نەدۆزرایەوە.")
            return

        messages.sort(key=lambda m: m.id)
        new_messages = [m for m in messages if m.id > last_id]

        if not new_messages:
            print("هیچ پۆستی نوێ نییە، هیچ شتێک نانێردرێت.")
            return

        for msg in new_messages:
            try:
                if msg.photo:
                    downloaded = app.download_media(msg.photo.file_id)
                    fitted_path = f"fitted_{msg.id}.jpg"
                    fit_to_story(downloaded, fitted_path)

                    app.send_story(
                        chat_id="me",
                        photo=fitted_path,
                        caption=msg.caption or "",
                    )
                    print(f"وێنەی پۆستی {msg.id} نێردرا بۆ ستۆری ✅")

                    os.remove(downloaded)
                    os.remove(fitted_path)

                elif msg.video:
                    app.send_story(
                        chat_id="me",
                        video=msg.video.file_id,
                        caption=msg.caption or "",
                    )
                    print(f"ڤیدیۆی پۆستی {msg.id} نێردرا بۆ ستۆری ✅")

                else:
                    print(f"پۆستی {msg.id} نە وێنە و نە ڤیدیۆیە، ڕەد کرا.")

                save_last_id(msg.id)

            except Exception as e:
                print(f"هەڵە لە ناردنی پۆستی {msg.id}: {e}")


if __name__ == "__main__":
    main()
