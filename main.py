import os
import asyncio
from flask import Flask
from threading import Thread
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from gradio_client import Client
from config import BOT_TOKEN, PORT

# --- FLASK SETUP ---
app = Flask(__name__)
@app.route('/')
def home(): return "Free Enhancer Bot is Running!"

def run_flask():
    app.run(host='0.0.0.0', port=PORT)

# --- BOT SETUP ---
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Hugging Face Client (CodeFormer - Best for Face & Quality)
# Isme API Key ki zaroorat nahi padti mostly
hf_client = Client("sczhou/CodeFormer")

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.reply("👋 Swagat hai! Main Hugging Face AI use kar raha hoon.\n\nImage bhejien aur magic dekhein!")

@dp.message(F.photo)
async def handle_photo(message: types.Message):
    builder = InlineKeyboardBuilder()
    # Humne data chhota rakha hai
    builder.row(types.InlineKeyboardButton(text="🚀 Enhance (Free)", callback_data="enhance_now"))
    
    await message.reply("Niche diye gaye button par click karein:", reply_markup=builder.as_markup())

@dp.callback_query(F.data == "enhance_now")
async def process_image(callback: types.CallbackQuery):
    # Check if it's a reply to a photo
    if not callback.message.reply_to_message or not callback.message.reply_to_message.photo:
        await callback.answer("❌ Photo nahi mili!", show_alert=True)
        return

    await callback.message.edit_text("⏳ Processing... Hugging Face AI thoda time leta hai (15-30s).")

    try:
        # 1. Image download link
        file_id = callback.message.reply_to_message.photo[-1].file_id
        file = await bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file.file_path}"

        # 2. AI Model ko call karna
        # CodeFormer parameters: [image, fidelity, background_enhance, face_upsample, upscale]
        result = hf_client.predict(
            file_url,   # image_path
            0.5,        # fidelity (0.1 to 1)
            True,       # background_enhance
            True,       # face_upsample
            2,          # upscale (2x)
            api_name="/predict"
        )

        # 3. Result bhej dena
        # 'result' ek local file path hota hai jo Gradio download karta hai
        await bot.send_photo(
            callback.from_user.id,
            photo=types.FSInputFile(result),
            caption="✅ Done! (Powered by CodeFormer AI)"
        )
        await callback.message.delete()

    except Exception as e:
        await callback.message.edit_text(f"❌ Error: {str(e)}")

async def main():
    # Start Flask for Render
    Thread(target=run_flask, daemon=True).start()
    # Start Bot
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
