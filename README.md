# View Once Downloader

Telegram userbot untuk menyimpan media **view once / self-destruct** ke Saved Messages.

## Cara Pakai

Balas pesan berisi media view once dengan `.dl` — media otomatis terkirim ke Saved Messages lengkap dengan mention pengirim.

## Environment Variables

| Variable | Keterangan |
|---|---|
| `API_ID` | Dari [my.telegram.org](https://my.telegram.org) |
| `API_HASH` | Dari [my.telegram.org](https://my.telegram.org) |
| `STRING_SESSION` | Generate pakai script di bawah |

## Generate STRING_SESSION

Jalankan script ini **sekali** di lokal:

```bash
pip install telethon
python -c "
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
api_id = int(input('API_ID: '))
api_hash = input('API_HASH: ')
with TelegramClient(StringSession(), api_id, api_hash) as c:
    print('STRING_SESSION:', c.session.save())
"
```

Salin output string tersebut sebagai nilai `STRING_SESSION`.

## Deploy ke Railway

1. Fork / connect repo ini ke [Railway](https://railway.app)
2. Set 3 environment variables di atas
3. Railway otomatis deploy — cek Logs untuk konfirmasi

## Catatan

- Hapus pesan asli hanya berhasil jika kamu **admin** di grup, atau di DM
- Media didownload ke memory (tidak perlu disk) — cocok untuk free tier Railway
