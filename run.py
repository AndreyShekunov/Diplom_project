import asyncio
from aiogram import Bot, Dispatcher
from app.handlers import router

import os
from dotenv import load_dotenv

load_dotenv()
bot = Bot(token=os.getenv("TOKEN"), parse_mode="HTML")
dp = Dispatcher()

async def start_bot():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(start_bot())
