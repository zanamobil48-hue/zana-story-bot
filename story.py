import os
import json
from pyrogram import Client

API_ID = int(os.environ.get("TELEGRAM_API_ID"))
API_HASH = os.environ.get("TELEGRAM_API_HASH")
SESSION_STRING = os.environ.get("TELEGRAM_SESSION_STRING")
CHANNEL_USERNAME = os.environ.get("TELEGRAM_CHANNEL", "Zanamobile1")

STATE_FILE = "last_message.json"


def load_last_id():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            data = json.load(f)
            return data.get("last_id", 0)
    return 0


def save_last_id(message_id: int):
    with open(STATE_FILE, "w") as f:
        json.dump({"last_id": message_id}, f)


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
                    app.send_story(
                        chat_id="me",
                        photo=msg.photo.file_id,
                        caption=msg.caption or "",
                    )
                    print(f"وێنەی پۆستی {msg.id} نێردرا بۆ ستۆری ✅")

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
                try:
                    import inspect
                    sig = inspect.signature(app.send_story)
                    print(f"شێوازی ڕاستەقینەی send_story: {sig}")
                except Exception as e2:
                    print(f"نەتوانرا signature ـی send_story وەربگیرێت: {e2}")


if __name__ == "__main__":
    main()
