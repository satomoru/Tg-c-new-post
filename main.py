from telethon.errors import PhoneNumberBannedError, PasswordHashInvalidError, UsernameInvalidError
from telethon.types import DocumentAttributeFilename, InputMediaUploadedPhoto
from telethon.sync import TelegramClient, events
import os
import re

from config import (API_ID,
                    API_HASH,
                    PHONE_NUMBER,
                    CHANNELS_COPY,
                    CHANNEL_PASTE,
                    DEVICE_MODEL,
                    SYSTEM_VERSION,
                    AUTO_DELETE_LINKS,
                    FORWARDS)

last_id_message = []

async def check_caption(caption):
    if AUTO_DELETE_LINKS is False:
        return caption
    elif AUTO_DELETE_LINKS is True:
        return re.sub(r'<a\s[^>]*>.*?</a>', '', caption)
    elif AUTO_DELETE_LINKS is None:
        return re.sub(r'<a\s[^>]*>(.*?)</a>', r'\1', caption)
    elif AUTO_DELETE_LINKS not in [True, False, None]:
        return re.sub(r'<a\s+(?:[^>]*?\s+)?href="([^"]*)"(?:[^>]*)>(.*?)</a>', rf'<a href="{AUTO_DELETE_LINKS}">\2</a>', caption)

client = TelegramClient(
    session = f"tg_{PHONE_NUMBER}",
    api_id = API_ID,
    api_hash = API_HASH,
    device_model = DEVICE_MODEL,
    system_version = SYSTEM_VERSION
)

@client.on(events.Album(CHANNELS_COPY))
async def album_handler(event):
    if FORWARDS is True:
        if event.messages[0].fwd_from:
            pass
        else:
            return
    elif FORWARDS is False:
        if event.messages[0].fwd_from:
            return

    media = []
    caption = event.messages[0].text
    force_document = False
    id = event.messages[0].id
    if id in last_id_message:
        last_id_message.clear()
        return
    last_id_message.append(id)

    caption = await check_caption(caption)

    print(f"Albom olindi:  {len(event)} ")
    
    for group_message in event.messages:
        if group_message.photo:
            media.append(await client.download_media(group_message, f"temp_pics/{group_message.id}.png"))
        elif group_message.video:
            media.append(await client.download_media(group_message, f"temp_pics/{group_message.id}.mp4"))
        elif group_message.document:
            file_name = next((x.file_name for x in group_message.document.attributes if isinstance(x, DocumentAttributeFilename)), None)
            media.append(await client.download_media(group_message, f"temp_pics/{file_name}"))
            force_document = True
        else:
            return bd_print("Noaniq malumot ! ")
    await client.send_file(CHANNEL_PASTE, media, caption=caption, force_document=force_document)
    print(f"Copy qilindi hamda yuborildi {len(event)}")
    
    for file in media:
        os.remove(file)

@client.on(events.NewMessage(CHANNELS_COPY, forwards=FORWARDS))
async def message_handler(event):
    if event.message.grouped_id is not None:
        return
    
    id = event.message.id
    caption = event.message.text
    spoiler = False
    web_preview = False
    
    try:
        if event.message.media.__dict__['spoiler'] is True:
            spoiler = True
    except AttributeError:
        pass
    except KeyError:
        pass

    try:
        if event.message.media.webpage.__dict__['url'] is not None:
            web_preview = True
    except AttributeError:
        pass
    except KeyError:
        pass

    print(f"habar qabul qilindi {id}.")

    caption = await check_caption(caption)

    if event.message.photo and not web_preview:
        await client.download_media(event.message, f"temp_pics/pics_{id}.png")
        await client.send_file(CHANNEL_PASTE, InputMediaUploadedPhoto(await client.upload_file(f"temp_pics/pics_{id}.png"), spoiler=spoiler), caption=caption)
        os.remove(f"temp_pics/pics_{id}.png")

    elif event.message.video: 
        await client.download_media(event.message, f"temp_pics/pics_{id}.mp4")
        await client.send_file(CHANNEL_PASTE, f"temp_pics/pics_{id}.mp4", caption=caption, video_note=True) 
        os.remove(f"temp_pics/pics_{id}.mp4")
        
    elif event.message.document:
        file_name = next((x.file_name for x in event.message.document.attributes if isinstance(x, DocumentAttributeFilename)), None)
        if event.message.document.mime_type == "audio/ogg":
            path = await client.download_media(event.message, f"temp_pics/{id}")
            await client.send_file(CHANNEL_PASTE, path, voice_note=True)
            os.remove(path)
            return
        await client.download_media(event.message, f"temp_pics/{file_name}")
        await client.send_file(CHANNEL_PASTE, f"temp_pics/{file_name}", caption=caption, force_document=True)
        os.remove(f"temp_pics/{file_name}")

    else:
        try:
            await client.send_message(CHANNEL_PASTE, caption)
        except Exception as e:
            bd_print(f"hatolik:  {e}")
            return

    print(f"copy qilindi hamda kanalingizga joylandi {id}.")

if __name__ == "__main__":
    try:
        client.start(phone=PHONE_NUMBER)
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print(f"accountingiz ulandi {PHONE_NUMBER}.")
        client.parse_mode = "html"

        client.run_until_disconnected()
        print(f"session {PHONE_NUMBER} succesed")
    except PhoneNumberBannedError:
        print(f"account {PHONE_NUMBER} blocklangan.")
    except PasswordHashInvalidError:
        print(f"hato parol {PHONE_NUMBER}.")
    except UsernameInvalidError:
        pass
    except Exception as e:
        print(f"noaniq hatolik:  {e}")