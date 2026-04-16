import os
import requests
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import InputFile
from pytube import YouTube
from aiogram.utils.markdown import hbold, hitalic

router = Router()

YOUTUBE_API_KEY = os.getenv("YT_API_KEY")

@router.message(Command("search"))
async def search_video(message: types.Message):
    query = message.text.replace("/search", "").strip()
    
    if not query:
        return await message.answer(f"Bhai, {hbold('Despacito')} jaise search query dalo!", parse_mode="HTML")

    status_msg = await message.answer(f"⏳ {hbold('Dhoondh raha hoon...')}", parse_mode="HTML")

    try:
        # YouTube API Search
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
            channel_title = video_data["snippet"]["channelTitle"]
            yt_link = f"https://www.youtube.com/watch?v={video_id}"

            # UI Update: Ab video stream kar rahe hain
            await status_msg.edit_text(f"⏳ {hitalic(title)} ko stream kar raha hoon...", parse_mode="HTML")

            # Pytube se stream link nikalna
            yt = YouTube(yt_link)
            stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
            
            if stream:
                stream_url = stream.url
                
                # Caption design
                caption_text = (
                    f"🎥 {hbold(title)}\n\n"
                    f"📺 Channel: {hitalic(channel_title)}\n\n"
                    f"👇 Play button dabayein, chat mein hi video enjoy karein!"
                )

                # Send_Video use karna native bubble play ke liye
                await message.reply_video(
                    video=stream_url,
                    caption=caption_text,
                    parse_mode="HTML"
                )
                
                await status_msg.delete()
            else:
                await status_msg.edit_text("❌ Streamable link nahi mila. Kuch aur try karein.")
        else:
            await status_msg.edit_text("❌ Kuch nahi mila.")
            
    except Exception as e:
        print(f"Error logic mein: {e}")
        await status_msg.edit_text(f"⚠️ Kuch error aaya: {e}")
        
