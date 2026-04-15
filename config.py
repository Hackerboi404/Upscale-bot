import os

# Plain text token hata do yahan se
BOT_TOKEN = os.environ.get("BOT_TOKEN")
HF_TOKEN = os.environ.get("HF_TOKEN")

PORT = int(os.environ.get("PORT", 5000))
