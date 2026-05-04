import os
import io
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.types import MessageMediaPhoto

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
STRING_SESSION = os.environ["STRING_SESSION"]

client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)


@client.on(events.NewMessage(outgoing=True, pattern=r"^\.dl$"))
async def dl_command(event):
    if not event.is_reply:
        await event.delete()
        return

    replied = await event.get_reply_message()

    if not replied.media:
        await event.delete()
        return

    # Ambil info pengirim
    sender = await replied.get_sender()
    if sender:
        name = f"{getattr(sender, 'first_name', '') or ''} {getattr(sender, 'last_name', '') or ''}".strip()
        if getattr(sender, "username", None):
            mention = f"@{sender.username}"
        else:
            mention = f"[{name or 'Unknown'}](tg://user?id={sender.id})"
    else:
        mention = "Unknown"

    chat = await event.get_chat()
    chat_title = getattr(chat, "title", None) or "Private Chat"

    caption = f"\U0001f4e5 **Dari:** {mention}\n\U0001f4ac **Chat:** {chat_title}"

    # Download ke memory
    try:
        media_bytes = await client.download_media(replied.media, bytes)
    except Exception as e:
        await event.delete()
        return

    if not media_bytes:
        await event.delete()
        return

    file_obj = io.BytesIO(media_bytes)

    # Tentukan nama file
    if isinstance(replied.media, MessageMediaPhoto):
        file_obj.name = "photo.jpg"
    else:
        fname = "media.mp4"
        try:
            for attr in replied.media.document.attributes:
                if hasattr(attr, "file_name"):
                    fname = attr.file_name
                    break
        except Exception:
            pass
        file_obj.name = fname

    # Kirim ke Saved Messages
    await client.send_file(
        "me",
        file=file_obj,
        caption=caption,
        parse_mode="markdown"
    )

    # Hapus dua arah
    try:
        await replied.delete()
    except Exception:
        pass
    await event.delete()


print("\u2705 Userbot aktif. Balas media view-once dengan .dl")
client.start()
client.run_until_disconnected()
