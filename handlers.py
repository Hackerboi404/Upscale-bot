import os
import requests
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

YOUTUBE_API_KEY = os.getenv("YT_API_KEY")

@router.message(Command("search"))
async def search_video(message: types.Message):
    query = message.text.replace("/search", "").strip()
    
    if not query:
        return await message.answer("🔍 Please enter something to search!")

    searching_msg = await message.answer("⚡ *Searching on YouTube...*", parse_mode="Markdown")

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
            channel = video_data["snippet"]["channelTitle"]
            link = f"https://www.youtube.com/watch?v={video_id}"
            
            # --- CUSTOM UI BUTTONS ---
            builder = InlineKeyboardBuilder()
            # In buttons se bot ka UI "App" jaisa lagega
            builder.row(types.InlineKeyboardButton(text="🎵 Full Song", url=link))
            builder.add(types.InlineKeyboardButton(text="📤 Share", url=f"https://t.me/share/url?url={link}"))
            builder.row(types.InlineKeyboardButton(text="🔥 More from this Channel", url=f"https://www.youtube.com/channel/{video_data['snippet']['channelId']}"))

            caption = (
                f"✨ *Now Playing: {title}*\n\n"
                f"👤 *Channel:* {channel}\n"
                f"💎 *Quality:* HD\n\n"
                f"🎬 _Click the play button on the video above to start inside the chat!_"
            )

            await searching_msg.delete()
            # Link pehle bhej rahe hain taaki Telegram preview (Player) trigger kare
            await message.answer(
                f"{link}\n\n{caption}", 
                parse_mode="Markdown",
                reply_markup=builder.as_markup()
            )
        else:
            await searching_msg.edit_text("❌ No results found.")
            
    except Exception as e:
        await searching_msg.edit_text(f"⚠️ API Error: Check if YT_API_KEY is correct.")
        
