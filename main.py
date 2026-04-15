import os
import asyncio
from flask import Flask
from threading import Thread
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
import replicate
from config import BOT_TOKEN, REPLICATE_API_TOKEN, PORT

# Replicate API Token set karein
os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN

# --- FLASK SETUP (For Render Port Binding) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive and running!"

def run_flask():
    app.run(host='0.0.0.0', port=PORT)

# --- BOT SETUP ---
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# 1. /start command
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    welcome_text = (
        "👋 Welcome to AI Image Enhancer!\n\n"
        "Main aapki low-quality photos ko HD mein badal sakta hoon.\n"
        "Shuru karne ke liye /upload command ka use karein."
    )
    await message.reply(welcome_text)

# 2. /upload command
@dp.message(Command("upload"))
async def upload_cmd(message: types.Message):
    await message.reply("📸 Please woh photo bhejein jise aap enhance karna chahte hain.")

# 3. Photo milne par Buttons dikhana
@dp.message(F.photo)
async def handle_photo(message: types.Message):
    # Callback data chhota rakha hai taaki 'BUTTON_DATA_INVALID' error na aaye
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="2x (720p Style)", callback_data="upscale_2"))
    builder.row(types.InlineKeyboardButton(text="4x (1080p/Ultra HD)", callback_data="upscale_4"))
    builder.row(types.InlineKeyboardButton(text="✨ Face Clean + 4x", callback_data="upscale_face"))
    
    await message.reply(
        "Quality select karein:", 
        reply_markup=builder.as_markup()
    )

# 4. Processing Logic (Jab button click ho)
@dp.callback_query(F.data.startswith("upscale_"))
async def process_image(callback: types.CallbackQuery):
    choice = callback.data.split("_")[1]
    
    # Check karein ki kya ye kisi photo ka reply hai
    if not callback.message.reply_to_message or not callback.message.reply_to_message.photo:
        await callback.answer("❌ Error: Original photo nahi mili. Dubara bhejien.", show_alert=True)
        return

    await callback.message.edit_text("⚡ AI Processing shuru... Isme thoda waqt lagta hai.")
    
    try:
        # File ID nikalna original photo se
        file_id = callback.message.reply_to_message.photo[-1].file_id
        file = await bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file.file_path}"
        
        # Scale aur Face logic set karna
        scale = 4 if choice in ["4", "face"] else 2
        face_fix = True if choice == "face" else False
        
        # Replicate AI model run karna
        output = replicate.run(
            "nightmareai/real-esrgan:42fed1c09745c7929424e6ca6f437c3756088d8b9d0739f723652873d6d5663a",
            input={
                "image": file_url,
                "upscale": scale,
                "face_enhance": face_fix
            }
        )
        
        # Result bhej dena
        await callback.message.delete() # 'Processing' message hatayein
        await bot.send_photo(
            callback.from_user.id, 
            photo=output, 
            caption=f"✅ Done!\n🚀 Scale: {scale}x\n👤 Face Fix: {'On' if face_fix else 'Off'}"
        )
        
    except Exception as e:
        await callback.message.edit_text(f"❌ Kuch galat ho gaya: {str(e)}")

# --- MAIN RUNNER ---
async def main():
    # Flask ko background thread mein start karein
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    print("Bot is starting...")
    # Bot polling shuru karein
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped.")
        
