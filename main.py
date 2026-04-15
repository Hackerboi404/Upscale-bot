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
def home(): return "Bot is running!"

def run_flask():
    app.run(host='0.0.0.0', port=PORT)

# --- BOT SETUP ---
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Hugging Face Client
client = Client("sczhou/CodeFormer", token=HF_TOKEN)

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.reply("👋 Swagat hai! Photo bhejein aur magic dekhein.")

@dp.message(F.photo)
async def handle_photo(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🚀 Enhance Now (Free)", callback_data="do_enhance"))
    await message.reply("Quality enhance karne ke liye niche click karein:", reply_markup=builder.as_markup())

@dp.callback_query(F.data == "do_enhance")
async def process_image(callback: types.CallbackQuery):
    if not callback.message.reply_to_message or not callback.message.reply_to_message.photo:
        return await callback.answer("❌ Error: Photo nahi mili!")

    await callback.message.edit_text("⏳ AI Processing... (It might take 30-60s)")

    try:
        # 1. Image ko local download karna (Zyada stable hai)
        file_id = callback.message.reply_to_message.photo[-1].file_id
        file_info = await bot.get_file(file_id)
        input_path = f"input_{file_id}.jpg"
        await bot.download_file(file_info.file_path, input_path)

        # 2. AI Model ko local file bhejiyega
        # CodeFormer params: [image, fidelity, background_enhance, face_upsample, upscale]
        job = client.submit(
            input_path, # Local file path
            0.7,        # Fidelity (0.7 results in better quality usually)
            True,       # background_enhance
            True,       # face_upsample
            2,          # upscale
            fn_index=0
        )
        result = job.result()

        # 3. Photo bhejna
        await bot.send_photo(
            callback.from_user.id,
            photo=FSInputFile(result),
            caption="✅ Done! Quality Improved."
        )
        
        # Cleanup: Local file delete karna
        if os.path.exists(input_path):
            os.remove(input_path)
            
        await callback.message.delete()

    except Exception as e:
        # Agar CodeFormer fail ho raha hai, toh user ko batayein
        await callback.message.edit_text(f"❌ AI Server Busy: {str(e)}\n\nThodi der baad dobara try karein.")
        if 'input_path' in locals() and os.path.exists(input_path):
            os.remove(input_path)

async def main():
    Thread(target=run_flask, daemon=True).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
