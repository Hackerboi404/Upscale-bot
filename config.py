import os

# Plain text token hata do yahan se
BOT_TOKEN = os.environ.get("BOT_TOKEN")
REPLICATE_API_TOKEN = os.environ.get("REPLICATE_API_TOKEN")

PORT = int(os.environ.get("PORT", 5000))
