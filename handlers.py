from aiogram import Router, types
from aiogram.filters import Command
from youtubesearchpython import VideosSearch

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Swaagat hai! 🎬\nBas `/search [gaana ya video]` likho aur chat mein hi video enjoy karo.")

@router.message(Command("search"))
async def search_video(message: types.Message):
    query = message.text.replace("/search", "").strip()
    
    if not query:
        return await message.answer("Bhai, kya search karna hai? Example: `/search animal movie trailer`")

    searching_msg = await message.answer("🔍 Dhoondh raha hoon...")

    try:
        # YouTube search (sirf 1 result uthayenge fast response ke liye)
        videos_search = VideosSearch(query, limit=1)
        results = videos_search.result()

        if results['result']:
            video = results['result'][0]
            title = video['title']
            link = video['link']
            duration = video['duration']
            views = video['viewCount']['short']
            
            # Caption design
            caption = (
                f"🎥 **{title}**\n\n"
                f"⏳ **Duration:** {duration}\n"
                f"👁‍🗨 **Views:** {views}\n\n"
                f"👇 Niche thumbnail pe 'Play' button dabayein!"
            )
            
            # Pehle wala "Searching" message delete karke link bhejenge
            await searching_msg.delete()
            await message.answer(f"{link}\n\n{caption}")
        else:
            await searching_msg.edit_text("❌ Kuch nahi mila, kuch aur try karo.")
            
    except Exception as e:
        await searching_msg.edit_text("⚠️ Kuch error aaya, thodi der baad try karein.")
        print(f"Error: {e}")
      
