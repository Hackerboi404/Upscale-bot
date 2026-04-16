import os
import requests
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest

router = Router()

YOUTUBE_API_KEY = os.getenv("YT_API_KEY")

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    # Welcome message in Hindi/Hinglish
    welcome_text = (
        "Swaagat hai bhai! ✨\n\n"
        "Main tumhare liye YouTube se videos dhoondh sakta hoon.\n\n"
        "🔍 *Kaise use karein?*\n"
        "Bas `/search [gaane ka naam]` likho.\n\n"
        "💡 *Pro Tip:* Video play hone ke baad upar 3-dots par click karke 'Minimize' kar dena, fir chat bhi kar paoge aur video bhi chalti rahegi!"
    )
    await message.answer(welcome_text, parse_mode="Markdown")

@router.message(Command("search"))
async def search_video(message: types.Message):
    query = message.text.replace("/search", "").strip()
    
    if not query:
        return await message.answer("Bhai, search query toh dalo! Example: `/search Arijit Singh`")

    searching_msg = await message.answer("🔍 Dhoondh raha hoon...")

    try:
        url = (
            f"https://www.googleapis.com/youtube/v3/search"
            f"?part=snippet&q={query}&maxResults=1&type=video&key={YOUTUBE_API_KEY}"
        )
        
        response = requests.get(url, timeout=10)
        data = response.json()

        if "items" in data and len(data["items"]) > 0:
            video_data = data["items"][0]
            video_id = video_data["id"]["videoId"]
            title = video_data["snippet"]["title"]
            link = f"https://www.youtube.com/watch?v={video_id}"
            
            # 3-dot minimize instruction added here
            caption = (
                f"🎥 *{title}*\n\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"✅ *Step 1:* Niche video play karein\.\n"
                f"✅ *Step 2:* Upar 3\-dots \(⋮\) par click karein\.\n"
                f"✅ *Step 3:* 'Minimize' select karein aur enjoy karein\! 🔥"
            )

            try:
                await searching_msg.delete()
            except TelegramBadRequest:
                pass 

            await message.answer(f"{link}\n\n{caption}", parse_mode="MarkdownV2")
            
        else:
            await message.answer("❌ Kuch nahi mila, naam sahi se check karo.")
            
    except Exception as e:
        print(f"Error occurred: {e}")
        await message.answer("⚠️ Kuch error aaya, thodi der baad try karein.")
        
