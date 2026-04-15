import os
import asyncio
from flask import Flask
from threading import Thread
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
import replicate
from config import BOT_TOKEN, REPLICATE_API_TOKEN, PORT

# API Token Set karein
os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN

# Flask Setup (Port Binding ke liye)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is Running!"

def run_flask():
    app.run(host='0.0.0.0', port=PORT)

# Bot Setup
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# /start command
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.reply("👋 Welcome! Main AI Image Enhancer hoon.\n\nAbhi /upload command ka use karein.")

# /upload command
@dp.message(Command("upload"))
async def upload_cmd(message: types.Message):
    await message.reply("📸 Please woh image bhejein jise aap enhance/upscale karna chahte hain.")

# Image handling aur Buttons
@dp.message(F.photo)
async def handle_photo(message: types.Message):
    photo_id = message.photo[-1].file_id
    
    builder = InlineKeyboardBuilder()
    # Callback data mein hum resolution aur file_id save kar rahe hain
    builder.row(types.InlineKeyboardButton(text="360p to 720p (2x)", callback_data=f"up_2_{photo_id}"))
    builder.row(types.InlineKeyboardButton(text="720p to 1080p (4x)", callback_data=f"up_4_{photo_id}"))
    builder.row(types.InlineKeyboardButton(text="Face Clean + 4x", callback_data=f"face_4_{photo_id}"))
    
    await message.reply("Resolution select karein jisme aapko output chahiye:", reply_markup=builder.as_markup())

# Processing Logic
@dp.callback_query(F.data.startswith(("up_", "face_")))
async def process_image(callback: types.CallbackQuery):
    data = callback.data.split("_")
    mode = data[0] # up ya face
    scale = int(data[1])
    file_id = data[2]
    
    await callback.message.edit_text("⏳ AI Processing shuru ho gayi hai... Isme 10-20 seconds lag sakte hain.")
    
    try:
        # 1. Image URL nikalna
        file = await bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file.file_path}"
        
        # 2. Replicate API call
        is_face = True if mode == "face" else False
        
        output = replicate.run(
            "nightmareai/real-esrgan:42fed1c09745c7929424e6ca6f437c3756088d8b9d0739f723652873d6d5663a",
            input={
                "image": file_url,
                "upscale": scale,
                "face_enhance": is_face
            }
        )
        
        # 3. Output bhejna
        await callback.message.delete()
        await bot.send_photo(
            callback.from_user.id, 
            photo=output, 
            caption=f"✅ Image Enhanced! Scale: {scale}x\nMode: {'Face Clean' if is_face else 'Standard'}"
        )
        
    except Exception as e:
        await callback.message.edit_text(f"❌ Error: {str(e)}")

# Bot Runner
async def main():
    # Flask ko background mein chalayein
    Thread(target=run_flask).start()
    # Bot polling shuru karein
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
  
