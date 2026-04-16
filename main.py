import asyncio
import logging
import os
from threading import Thread
from flask import Flask
from aiogram import Dispatcher, Bot
from config import BOT_TOKEN
from handlers import router

# 1. Flask App Setup (Render ke liye)
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Bot is Running Live!", 200

def run_flask():
    # Render default port 10000 use karta hai
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# 2. Bot Setup
async def run_bot():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    
    print("Bot polling start ho rahi hai...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    # Flask ko background thread mein chalana
    Thread(target=run_flask).start()
    
    # Bot ko main thread mein chalana
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        print("Bot stopped.")
        
