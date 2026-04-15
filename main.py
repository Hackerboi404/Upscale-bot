import os
import asyncio
from flask import Flask
from threading import Thread
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from gradio_client import Client
from aiogram.types import FSInputFile
from config import BOT_TOKEN, HF_TOKEN, PORT

# --- FLASK SETUP ---
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is running perfectly!"

def run_flask():
    app.run(host='0.0.0.0', port=PORT)

# --- BOT SETUP ---
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# FIXED: 'hf_token' renamed to 'token'
client = Client("sczhou/CodeFormer", token=HF_TOKEN)

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.reply("👋 Swagat hai! Photo bhejein aur magic dekhein.")

@dp.message(F.photo)
async def handle_photo(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🚀 Enhance Now (Free)", callback_data="do_enhance"))
    await message.reply("Click karein:", reply_markup=builder.as_markup())

@dp.callback_query(F.data == "do_enhance")
async def process_image(callback: types.CallbackQuery):
    if not callback.message.reply_to_message or not callback.message.reply_to_message.photo:
        return await callback.answer("Photo nahi mili!")

    await callback.message.edit_text("⏳ Processing... (Hugging Face AI)")

    try:
        file_id = callback.message.reply_to_message.photo[-1].file_id
        file = await bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file.file_path}"

        # Processing...
        job = client.submit(
            file_url,   # image
            0.5,        # fidelity
            True,       # background_enhance
            True,       # face_upsample
            2,          # upscale
            fn_index=0
        )
        result = job.result()

        await bot.send_photo(
            callback.from_user.id,
            photo=FSInputFile(result),
            caption="✅ Done! Powered by CodeFormer"
        )
        await callback.message.delete()

    except Exception as e:
        await callback.message.edit_text(f"❌ Error: {str(e)}")

async def main():
    Thread(target=run_flask, daemon=True).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
