import os
import requests
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest

router = Router()

YOUTUBE_API_KEY = os.getenv("YT_API_KEY")

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    # Welcome message in HTML (More stable)
    welcome_text = (
        "<b>Swaagat hai bhai!</b> ✨\n\n"
        "Main tumhare liye YouTube se videos dhoondh sakta hoon.\n\n"
        "🔍 <b>Kaise use karein?</b>\n"
        "Bas <code>/search gaane ka naam</code> likho.\n\n"
        "💡 <b>Pro Tip:</b> Video play hone ke baad upar 3-dots par click karke 'Minimize' kar dena, fir chat bhi kar paoge aur video bhi chalti rahegi!"
    )
    await message.answer(welcome_text, parse_mode="HTML")

@router.message(Command("search"))
async def search_video(message: types.Message):
    query = message.text.replace("/search", "").strip()
    
    if not query:
        return await message.answer("Bhai, search query toh dalo! Example: <code>/search Arijit Singh</code>", parse_mode="HTML")

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
            
            # Instruction message with clear steps
            caption = (
                f"🎥 <b>{title}</b>\n\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"✅ <b>Step 1:</b> Niche video play karein.\n"
                f"✅ <b>Step 2:</b> Upar 3-dots (⋮) par click karein.\n"
                f"✅ <b>Step 3:</b> 'Minimize' select karein aur enjoy karein! 🔥"
            )

            try:
                await searching_msg.delete()
            except TelegramBadRequest:
                pass 

            # Link aur caption bhej rahe hain (HTML mode mein)
            await message.answer(f"{link}\n\n{caption}", parse_mode="HTML")
            
        else:
            await searching_msg.edit_text("❌ Kuch nahi mila, naam sahi se check karo.")
            
    except Exception as e:
        print(f"Error occurred: {e}")
        # Agar error aaye toh purane message ko edit karke error dikhao (debugging ke liye)
        try:
            await searching_msg.edit_text(f"⚠️ Error: {str(e)[:50]}")
        except:
            await message.answer("⚠️ Kuch technical issue hai.")
            
