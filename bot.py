import re
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from config import BOT_TOKEN, CHANNEL_ID
from db import search_books, upsert_book, ensure_schema
from wiki import get_reading_order

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

async def is_member(user_id):
    try:
        m = await bot.get_chat_member(CHANNEL_ID, user_id)
        return m.status != "left"
    except:
        return False

@dp.message_handler(commands=["start"])
async def start(msg):
    await msg.reply(
        "/search <book>\n"
        "/order <series>"
    )

@dp.message_handler(commands=["search"])
async def search(msg):
    if not await is_member(msg.from_user.id):
        await msg.reply("Join library channel first.")
        return

    q = msg.get_args()
    if not q:
        return

    res = search_books(q)
    if not res:
        await msg.reply("No books found.")
        return

    for title, topic, mid in res:
        await bot.forward_message(msg.chat.id, CHANNEL_ID, mid)

@dp.message_handler(commands=["order"])
async def order(msg):
    q = msg.get_args()
    if not q:
        return

    txt = get_reading_order(q)
    await msg.reply(txt or "Not found.")

def _extract_title(message: types.Message) -> str:
    if message.caption:
        line = message.caption.splitlines()[0].strip()
        if line:
            return line
    if message.document and message.document.file_name:
        name = message.document.file_name
        return name.rsplit(".", 1)[0]
    return "Untitled"

def _extract_topic(message: types.Message):
    if message.caption:
        match = re.search(r"#([\w-]+)", message.caption)
        if match:
            return match.group(1).replace("_", " ")
    if message.message_thread_id:
        return f"topic-{message.message_thread_id}"
    return None

@dp.channel_post_handler(content_types=types.ContentTypes.DOCUMENT)
async def index_channel_book(message: types.Message):
    if message.chat.id != CHANNEL_ID:
        return

    if message.document and message.document.file_name:
        fname = message.document.file_name.lower()
        if not (fname.endswith(".pdf") or fname.endswith(".epub")):
            return

    title = _extract_title(message)
    topic = _extract_topic(message)
    upsert_book(title, topic, message.message_id)

if __name__ == "__main__":
    ensure_schema()
    executor.start_polling(dp)
