import os
import io
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
STRING_SESSION = os.environ["STRING_SESSION"]

client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)


def escape_md(text: str) -> str:
    if not text:
        return "Unknown"
    for ch in ["[", "]", "(", ")", "*", "_", "`"]:
        text = text.replace(ch, f"\\{ch}")
    return text


def is_view_once(message) -> bool:
    """Cek apakah media adalah view once (ttl & noforwards)"""
    media = message.media
    if isinstance(media, MessageMediaPhoto):
        return bool(getattr(media, "ttl_seconds", None))
    if isinstance(media, MessageMediaDocument):
        return bool(getattr(media, "ttl_seconds", None))
    return False


def is_timer(message) -> bool:
    """Cek apakah media adalah timer (noforwards tapi bisa forward via API)"""
    if is_view_once(message):
        return False
    media = message.media
    if isinstance(media, (MessageMediaPhoto, MessageMediaDocument)):
        return bool(getattr(message, "noforwards", False))
    return False


@client.on(events.NewMessage(outgoing=True, pattern=r"^\.dl$"))
async def dl_command(event):
    # Hapus command .dl LANGSUNG, tidak menunggu proses selesai
    await event.delete()

    if not event.is_reply:
        return

    replied = await event.get_reply_message()

    if not replied or not replied.media:
        return

    # Ambil info pengirim
    sender = await replied.get_sender()
    if sender:
        first_name = getattr(sender, "first_name", "") or ""
        last_name = getattr(sender, "last_name", "") or ""
        display_name = (f"{first_name} {last_name}").strip() or "Unknown"
        display_name = escape_md(display_name)
        mention = f"[{display_name}](tg://user?id={sender.id})"
    else:
        mention = "Unknown"

    chat = await event.get_chat()
    chat_title = escape_md(getattr(chat, "title", None) or "Private Chat")
    caption = f"\U0001f4e5 **Dari:** {mention}\n\U0001f4ac **Chat:** {chat_title}"

    # --- METODE FORWARD (untuk timer media) ---
    if is_timer(replied):
        try:
            await client.forward_messages("me", replied)
            # Kirim caption terpisah karena forward tidak bisa custom caption
            await client.send_message("me", caption, parse_mode="markdown")
        except Exception:
            pass
        return

    # --- METODE MANUAL (untuk view once) ---
    try:
        media_bytes = await client.download_media(replied.media, bytes)
    except Exception:
        return

    if not media_bytes:
        return

    file_obj = io.BytesIO(media_bytes)

    if isinstance(replied.media, MessageMediaPhoto):
        file_obj.name = "photo.jpg"
    else:
        fname = "media.mp4"
        try:
            for attr in replied.media.document.attributes:
                if hasattr(attr, "file_name") and attr.file_name:
                    fname = attr.file_name
                    break
        except Exception:
            pass
        file_obj.name = fname

    await client.send_file(
        "me",
        file=file_obj,
        caption=caption,
        parse_mode="markdown"
    )


print("\u2705 Userbot aktif. Balas media view-once/timer dengan .dl")
client.start()
client.run_until_disconnected()
