import os
import asyncio
from flask import Flask
from threading import Thread
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from gradio_client import Client
from config import BOT_TOKEN, PORT

# Flask Setup
app = Flask(__name__)
@app.route('/')
def home(): return "Free Bot is Running!"

def run_flask():
    app.run(host='0.0.0.0', port=PORT)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Hugging Face Client Setup
# Hum CodeFormer use kar rahe hain jo face aur quality dono ke liye best hai
client = Client("sczhou/CodeFormer")

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.reply("👋 Free AI Enhancer! Photo bhejein aur magic dekhein.")

@dp.message(F.photo)
async def handle_photo(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="Enhance Photo (Free)", callback_data="free_up"))
    await message.reply("Niche click karein:", reply_markup=builder.as_markup())

@dp.callback_query(F.data == "free_up")
async def process_free(callback: types.CallbackQuery):
    if not callback.message.reply_to_message or not callback.message.reply_to_message.photo:
        return await callback.answer("Photo nahi mili!")

    await callback.message.edit_text("⏳ Hugging Face AI processing... (Free)")

    try:
        file_id = callback.message.reply_to_message.photo[-1].file_id
        file = await bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file.file_path}"

        # Hugging Face Model Call
        # Parameters: image, codeformer_fidelity, background_enhance, face_upsample, upscale
        result = client.predict(
            file_url,	# image
            0.5,		# fidelity (0 to 1)
            True,		# background enhance
            True,		# face upsample
            2,			# upscale (2x)
            api_name="/predict"
        )

        # Result 'result' ek path hota hai file ka
        await bot.send_photo(
            callback.from_user.id,
            photo=types.FSInputFile(result),
            caption="✅ Done! (Powered by Hugging Face)"
        )
        await callback.message.delete()

    except Exception as e:
        await callback.message.edit_text(f"❌ Error: {str(e)}")

async def main():
    Thread(target=run_flask, daemon=True).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
