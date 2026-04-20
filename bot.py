from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import aiosqlite
import time

BOT_TOKEN = "8269708585:AAHt0ijMphvwwsSsV74UrjCQ3b5FhrwuS5I"
ADMIN_ID = 7273500546

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

last_used = {}

# DATABASE
async def init_db():
    async with aiosqlite.connect("database.db") as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            balance REAL DEFAULT 0
        )
        """)
        await db.commit()

async def add_user(user_id):
    async with aiosqlite.connect("database.db") as db:
        await db.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (user_id,))
        await db.commit()

async def get_balance(user_id):
    async with aiosqlite.connect("database.db") as db:
        cursor = await db.execute("SELECT balance FROM users WHERE id = ?", (user_id,))
        result = await cursor.fetchone()
        return result[0] if result else 0

async def add_balance(user_id, amount):
    async with aiosqlite.connect("database.db") as db:
        await db.execute("UPDATE users SET balance = balance + ? WHERE id = ?", (amount, user_id))
        await db.commit()

# START
@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    await add_user(msg.from_user.id)
    await msg.answer("Bot ishlayapti ✅\n/add\n/balance")

# BALANCE
@dp.message_handler(commands=["balance"])
async def balance(msg: types.Message):
    bal = await get_balance(msg.from_user.id)
    await msg.answer(f"Balans: {bal}$")

# ADD
@dp.message_handler(commands=["add"])
async def add(msg: types.Message):
    user_id = msg.from_user.id
    now = time.time()

    if user_id in last_used and now - last_used[user_id] < 5:
        await msg.answer("Kut ⏳")
        return

    last_used[user_id] = now

    await add_balance(user_id, 5)
    await msg.answer("5$ qo‘shildi")

# TEST
@dp.message_handler()
async def echo(msg: types.Message):
    await msg.answer("Ishlayapman ✅")

# STARTUP
async def on_startup(_):
    await bot.delete_webhook(drop_pending_updates=True)
    await init_db()
    print("Bot ishga tushdi!")

if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup)