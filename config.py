import os
from dotenv import load_dotenv

load_dotenv()

# Token ko environment variable se uthayenge
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    exit("Error: BOT_TOKEN nahi mila! .env file check karein.")
  
