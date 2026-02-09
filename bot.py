from aiogram import Bot, Dispatcher
from aiogram.utils import executor
from config import BOT_TOKEN, CHANNEL_ID
from db import search_books
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

if __name__ == "__main__":
    executor.start_polling(dp)
