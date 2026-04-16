import os
import urllib.parse
from openai import OpenAI
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

# --- CONFIGURATION ---
# Render Dashboard mein 'HF_TOKEN' set karein
HF_TOKEN = os.environ.get("HF_TOKEN")

# OpenAI-compatible Client for Hugging Face
client = None
if HF_TOKEN:
    client = OpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=HF_TOKEN,
    )

# --- UI DESIGN (Premium Glassmorphism) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>OmniAI - Smart Engine</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background: #020617; color: white; font-family: sans-serif; overflow: hidden; height: 100vh; }
        .glass { background: rgba(15, 23, 42, 0.75); backdrop-filter: blur(25px); border: 1px solid rgba(255,255,255,0.1); }
        .chat-area { height: calc(100vh - 180px); overflow-y: auto; scroll-behavior: smooth; }
        .msg-card { background: rgba(30, 41, 59, 0.5); border: 1px solid rgba(255,255,255,0.05); transition: all 0.3s; }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 10px; }
    </style>
</head>
<body class="flex items-center justify-center p-3 md:p-6">
    <div class="glass w-full max-w-2xl rounded-[2.5rem] p-5 md:p-8 flex flex-col h-[95vh]">
        <header class="text-center mb-4">
            <h1 class="text-3xl font-black tracking-tight italic">Omni<span class="text-blue-500">AI</span></h1>
            <p class="text-[9px] text-slate-500 uppercase tracking-widest">MiniMax + Pollinations Hybrid</p>
        </header>

        <div id="chat" class="chat-area space-y-4 mb-4 pr-1">
            <div class="msg-card p-4 rounded-2xl text-sm text-slate-300">Ready! Try asking: "Generate a neon car photo"</div>
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
                    div.innerHTML = `
                        <p class="text-[10px] text-blue-400 font-bold mb-2 uppercase tracking-tighter italic">AI Generated Image</p>
                        <img src="${data.result}" class="w-full h-auto rounded-xl shadow-lg" loading="lazy">`;
                } else {
                    div.innerHTML = `<p class="text-sm leading-relaxed text-slate-200">${data.result}</p>`;
                }
                chat.appendChild(div);
                chat.scrollTop = chat.scrollHeight;
            } catch(e) {
                const errDiv = document.createElement('div');
                errDiv.className = "p-4 rounded-2xl bg-red-900/20 text-red-400 text-xs";
                errDiv.innerText = "Error: Token issue or server timeout.";
                chat.appendChild(errDiv);
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
    
    # Ye keywords check karenge ki user photo chahta hai ya nahi
    img_keywords = ["image", "photo", "banao", "picture", "logo", "wallpaper", "generate", "create", "drawing", "pic"]

    try:
        # LOGIC 1: Agar image keyword hai, toh AI ko call hi mat karo
        if any(word in text for word in img_keywords):
            encoded = urllib.parse.quote(prompt)
            # Har baar alag image ke liye seed change
            seed = os.urandom(2).hex()
            image_url = f"https://pollinations.ai/p/{encoded}?width=1024&height=1024&nologo=true&seed={seed}"
            return {"type": "image", "result": image_url}
        
        # LOGIC 2: Agar normal chat hai, toh Hugging Face use karo
        else:
            if not client:
                return {"type": "text", "result": "Error: HF_TOKEN set nahi hai dashboard mein!"}
            
            completion = client.chat.completions.create(
                model="MiniMaxAI/MiniMax-M2.7:together",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
            ai_reply = completion.choices[0].message.content
            return {"type": "text", "result": ai_reply}

    except Exception as e:
        return {"type": "text", "result": f"Execution Error: {str(e)}"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
    
