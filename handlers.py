import os
import requests
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest

router = Router()

YOUTUBE_API_KEY = os.getenv("YT_API_KEY")

@router.message(Command("search"))
async def search_video(message: types.Message):
    query = message.text.replace("/search", "").strip()
    
    if not query:
        return await message.answer("Bhai, search query toh dalo!")

    # Initial message
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
            
            caption = f"🎥 *{title}*\n\n👇 Play button pe click karein\!"

            # Sabse pehle purana message delete karne ki koshish karo
            try:
                await searching_msg.delete()
            except TelegramBadRequest:
                pass # Agar pehle se delete ho gaya toh koi baat nahi

            # Naya message link ke saath bhejo
            # Note: Link pehle bhej rahe hain taaki Telegram preview pakad le
            await message.answer(f"{link}\n\n{caption}", parse_mode="MarkdownV2")
            
        else:
            # Edit karne mein aksar error aata hai, isliye answer bhej dena safe hai
            await message.answer("❌ Kuch nahi mila.")
            
    except Exception as e:
        print(f"Error occurred: {e}")
        # Agar error aaye toh naya message bhej do, edit ke chakkar mein mat pado
        await message.answer("⚠️ Kuch error aaya, thodi der baad try karein.")
        
