import asyncio
import logging
import os
from threading import Thread
from flask import Flask
from aiogram import Dispatcher, Bot
from config import BOT_TOKEN
from handlers import router

# Render ke liye Flask App
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Bot is Running!", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# Bot Logic
async def run_bot():
    logging.basicConfig(level=logging.INFO)
    
    # Bot initialization
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    # Handlers register karna
    dp.include_router(router)
    
    print("🚀 Bot is starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    # Flask ko alag thread mein chalayein
    Thread(target=run_flask, daemon=True).start()
    
    # Bot ko main loop mein chalayein
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        print("Bot off ho gaya.")
        
