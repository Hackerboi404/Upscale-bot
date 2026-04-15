import os

# Render ke 'Environment' tab mein ye keys add karna zaroori hai
BOT_TOKEN = os.environ.get("BOT_TOKEN")
HF_TOKEN = os.environ.get("HF_TOKEN")

# Render automatically PORT deta hai, default 5000
PORT = int(os.environ.get("PORT", 5000))
