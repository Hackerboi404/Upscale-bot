import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN")

# YouTube API Key (Jo Google Cloud se mili hai)
YT_API_KEY = os.getenv("YT_API_KEY")

if not BOT_TOKEN:
    print("❌ Error: BOT_TOKEN nahi mila!")
if not YT_API_KEY:
    print("⚠️ Warning: YT_API_KEY set nahi hai. Search kaam nahi karega.")
    
