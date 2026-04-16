import os
import requests
from aiogram import Router, types
from aiogram.filters import Command

router = Router()

# API Key environment variable se le rahe hain
YOUTUBE_API_KEY = os.getenv("YT_API_KEY")

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Swaagat hai! 🎬\nBas `/search [video name]` likho aur enjoy karo.")

@router.message(Command("search"))
async def search_video(message: types.Message):
    # Search query nikalna
    query = message.text.replace("/search", "").strip()
    
    if not query:
        return await message.answer("Bhai, kya search karna hai? Example: `/search Arijit Singh`")

    if not YOUTUBE_API_KEY:
        return await message.answer("⚠️ API Key set nahi hai Render dashboard mein.")

    searching_msg = await message.answer("🔍 Dhoondh raha hoon...")

    try:
        # YouTube API Call
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
            channel = video_data["snippet"]["channelTitle"]
            link = f"https://www.youtube.com/watch?v={video_id}"
            
            # Simple Markdown string (Fixed 'as_markdown' error)
            caption = (
                f"🎥 *{title}*\n\n"
                f"📺 Channel: _{channel}_\n\n"
                f"👇 Niche thumbnail pe 'Play' button dabayein!"
            )
            
            # Message delete karke naya message bhejna
            await searching_msg.delete()
            # Yahan humne parse_mode="Markdown" use kiya hai
            await message.answer(f"{link}\n\n{caption}", parse_mode="Markdown")
        else:
            await searching_msg.edit_text("❌ Kuch nahi mila, kuch aur try karo.")
            
    except Exception as e:
        print(f"Error logic mein: {e}")
        # Error handling ko safe banana
        try:
            await searching_msg.edit_text("⚠️ Kuch error aaya, thodi der baad try karein.")
        except:
            await message.answer("⚠️ Kuch error aaya.")
            
