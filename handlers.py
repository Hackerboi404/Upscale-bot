import os
import requests
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.utils.formatting import Text, Bold, Italic

router = Router()

# API Key environment variable se le rahe hain
YOUTUBE_API_KEY = os.getenv("YT_API_KEY")

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Swaagat hai! 🎬\nBas `/search [gaana ya video]` likho aur chat mein hi video enjoy karo.")

@router.message(Command("search"))
async def search_video(message: types.Message):
    query = message.text.replace("/search", "").strip()
    
    if not query:
        return await message.answer("Bhai, kya search karna hai? Example: `/search animal movie trailer`")

    # API key check - agar Render pe set nahi ki hai toh
    if not YOUTUBE_API_KEY:
        print("Error: YT_API_KEY environment variable mein nahi mili.")
        return await message.answer("⚠️ Bot configuration mein issue hai. Developer se contact karein.")

    searching_msg = await message.answer("🔍 Dhoondh raha hoon...")

    try:
        # Official YouTube API URL - hum sasti API call kar rahe hain (1 point)
        url = (
            f"https://www.googleapis.com/youtube/v3/search"
            f"?part=snippet&q={query}&maxResults=1&type=video&key={YOUTUBE_API_KEY}"
        )
        
        response = requests.get(url, timeout=10)
        data = response.json()

        # Pehle check karo API ne koi error toh nahi diya (quota issue etc.)
        if "error" in data:
            print(f"YouTube API Error: {data['error']['message']}")
            await searching_msg.edit_text("⚠️ YouTube API mein kuch dikkat hai. Thodi der baad try karein.")
            return

        # Check karo result mila ya nahi
        if "items" in data and len(data["items"]) > 0:
            video_data = data["items"][0]
            video_id = video_data["id"]["videoId"]
            title = video_data["snippet"]["title"]
            channel = video_data["snippet"]["channelTitle"]
            link = f"https://www.youtube.com/watch?v={video_id}"
            
            # Message formatting
            caption = (
                f"🎥 {Bold(title)}\n\n"
                f"📺 Channel: {Italic(channel)}\n\n"
                f"👇 Niche thumbnail pe 'Play' button dabayein!"
            )
            
            # Link pehle bhej rahe hain taaki Telegram preview generate kare
            await searching_msg.delete()
            await message.answer(f"{link}\n\n{caption.as_markdown()}", parse_mode="MarkdownV2")
        else:
            await searching_msg.edit_text("❌ Kuch nahi mila, kuch aur try karo.")
            
    except requests.exceptions.RequestException as e:
        print(f"Network Error: {e}")
        await searching_msg.edit_text("⚠️ Network issue. Please thodi der baad try karein.")
    except Exception as e:
        print(f"Unexpected Error: {e}")
        await searching_msg.edit_text("⚠️ Kuch unexpected error aaya.")
        
