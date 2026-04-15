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

# --- FLASK SETUP (For Render) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is active and running for free!"

def run_flask():
    app.run(host='0.0.0.0', port=PORT)

# --- BOT SETUP ---
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Hugging Face Client Setup
# Token optional hai par dena behtar hai stability ke liye
client = Client("sczhou/CodeFormer", hf_token=HF_TOKEN)

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.reply(
        "👋 Swagat hai! Main ek Free AI Image Enhancer hoon.\n\n"
        "Shuru karne ke liye /upload likhein ya direct photo bhejein."
    )

@dp.message(Command("upload"))
async def upload_cmd(message: types.Message):
    await message.reply("📸 Photo bhejein jise aapne upscale/enhance karna hai.")

@dp.message(F.photo)
async def handle_photo(message: types.Message):
    builder = InlineKeyboardBuilder()
    # Simple logic: Ek hi button rakhte hain jo best setting apply karega
    builder.row(types.InlineKeyboardButton(text="🚀 Enhance Now (Free)", callback_data="do_enhance"))
    
    await message.reply("Niche button par click karke processing shuru karein:", reply_markup=builder.as_markup())

@dp.callback_query(F.data == "do_enhance")
async def process_image(callback: types.CallbackQuery):
    # Check if this is a reply to the original photo
    if not callback.message.reply_to_message or not callback.message.reply_to_message.photo:
        await callback.answer("❌ Error: Photo nahi mili. Dubara bhejein.", show_alert=True)
        return

    await callback.message.edit_text("⏳ AI Kaam kar raha hai... Isme 20-40 seconds lag sakte hain.")

    try:
        # 1. Image URL nikalna
        file_id = callback.message.reply_to_message.photo[-1].file_id
        file = await bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file.file_path}"

        # 2. Hugging Face Call (Using fn_index=0 to avoid API name errors)
        # CodeFormer parameters: image, fidelity, background_enhance, face_upsample, upscale
        job = client.submit(
            file_url,   # image
            0.5,        # fidelity (quality balance)
            True,       # background_enhance
            True,       # face_upsample
            2,          # upscale (2x)
            fn_index=0
        )
        
        # Result ka wait karein
        result = job.result()

        # 3. Result wapas bhejna
        # result variable mein image file ka local path hota hai
        photo_to_send = FSInputFile(result)
        
        await bot.send_photo(
            callback.from_user.id,
            photo=photo_to_send,
            caption="✅ Done! Image quality enhance ho gayi hai.\nPowered by CodeFormer AI"
        )
        await callback.message.delete()

    except Exception as e:
        await callback.message.edit_text(f"❌ Error: {str(e)}\n\nHo sakta hai server busy ho, thodi der baad try karein.")

async def main():
    # Flask ko background mein chalana
    Thread(target=run_flask, daemon=True).start()
    # Bot polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
        
