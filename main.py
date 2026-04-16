import os
import urllib.parse
from openai import OpenAI
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

# --- CONFIGURATION ---
# Render dashboard mein 'HF_TOKEN' set karein
HF_TOKEN = os.environ.get("HF_TOKEN")

# OpenAI-compatible Client for Hugging Face (Chat API)
client = None
if HF_TOKEN:
    client = OpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=HF_TOKEN,
    )

# --- UI DESIGN (Fixed Image Display) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>OmniAI - Ultra Fixed</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background: #020617; color: white; font-family: sans-serif; overflow: hidden; height: 100vh; }
        .glass { background: rgba(15, 23, 42, 0.75); backdrop-filter: blur(25px); border: 1px solid rgba(255,255,255,0.1); }
        .chat-area { height: calc(100vh - 180px); overflow-y: auto; scroll-behavior: smooth; }
        .msg-card { background: rgba(30, 41, 59, 0.5); border: 1px solid rgba(255,255,255,0.05); }
        .img-box { min-height: 200px; background: #0f172a; border-radius: 1rem; position: relative; }
        .loader-spin { border: 3px solid #1e293b; border-top: 3px solid #3b82f6; border-radius: 50%; width: 24px; height: 24px; animation: spin 1s linear infinite; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
</head>
<body class="flex items-center justify-center p-3 md:p-6">
    <div class="glass w-full max-w-2xl rounded-[2.5rem] p-5 md:p-8 flex flex-col h-[95vh]">
        <header class="text-center mb-4">
            <h1 class="text-3xl font-black italic">Omni<span class="text-blue-500">AI</span></h1>
            <p class="text-[9px] text-slate-500 uppercase tracking-widest">Chat: HF | Image: Pollinations</p>
        </header>

        <div id="chat" class="chat-area space-y-4 mb-4 pr-1">
            <div class="msg-card p-4 rounded-2xl text-sm text-slate-300 italic">Try: "Cyberpunk car ki photo banao"</div>
        </div>

        <div class="relative mt-auto">
            <input type="text" id="userInput" placeholder="Ask or command..." 
                class="w-full bg-slate-950/80 border border-slate-800 rounded-2xl py-4 px-5 pr-20 outline-none focus:border-blue-500 transition-all text-white">
            <button onclick="send()" id="sendBtn" class="absolute right-2 top-2 bottom-2 bg-blue-600 px-5 rounded-xl font-bold hover:bg-blue-500 active:scale-95 transition-all">Run</button>
        </div>
    </div>

    <script>
        async function send() {
            const input = document.getElementById('userInput');
            const chat = document.getElementById('chat');
            const btn = document.getElementById('sendBtn');
            const text = input.value.trim();
            if(!text) return;

            input.value = '';
            btn.disabled = true;
            btn.innerText = '...';

            const formData = new FormData();
            formData.append('prompt', text);

            try {
                const res = await fetch('/ask', { method: 'POST', body: formData });
                const data = await res.json();
                
                const div = document.createElement('div');
                div.className = "msg-card p-4 rounded-2xl animate-in fade-in slide-in-from-bottom-2 duration-300";
                
                if(data.type === 'image') {
                    // Yahan humne error handling daali hai taaki broken icon na dikhe
                    div.innerHTML = `
                        <p class="text-[10px] text-blue-400 font-bold mb-2 uppercase italic tracking-widest">Image Engine</p>
                        <div class="img-box flex items-center justify-center">
                            <img src="${data.result}" class="w-full h-auto rounded-xl shadow-2xl" 
                                 onload="this.previousElementSibling ? this.previousElementSibling.remove() : null"
                                 onerror="this.src='https://via.placeholder.com/500?text=Image+Generation+Failed'">
                        </div>`;
                } else {
                    div.innerHTML = `<p class="text-sm leading-relaxed text-slate-200">${data.result}</p>`;
                }
                chat.appendChild(div);
                chat.scrollTop = chat.scrollHeight;
            } catch(e) {
                console.error(e);
            } finally {
                btn.disabled = false;
                btn.innerText = 'Run';
            }
        }
    </script>
</body>
</html>
"""

# --- BACKEND ROUTES ---

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML_TEMPLATE

@app.post("/ask")
async def handle_request(prompt: str = Form(...)):
    text = prompt.lower()
    
    # Keywords check
    img_keywords = ["image", "photo", "banao", "picture", "logo", "wallpaper", "generate", "create", "pic"]

    try:
        # LOGIC: 2 APIs ka use
        if any(word in text for word in img_keywords):
            # API 1: Pollinations for Images
            # Important: Hindi prompts ke liye quote zaroori hai
            safe_prompt = urllib.parse.quote(prompt)
            seed = os.urandom(2).hex()
            image_url = f"https://pollinations.ai/p/{safe_prompt}?width=1024&height=1024&nologo=true&seed={seed}"
            return {"type": "image", "result": image_url}
        
        else:
            # API 2: Hugging Face (MiniMax) for Chat
            if not client:
                return {"type": "text", "result": "Error: HF_TOKEN missing in Render Env!"}
            
            completion = client.chat.completions.create(
                model="MiniMaxAI/MiniMax-M2.7:together",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=700
            )
            return {"type": "text", "result": completion.choices[0].message.content}

    except Exception as e:
        return {"type": "text", "result": f"System Error: {str(e)}"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
    
