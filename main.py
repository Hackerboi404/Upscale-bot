import os
import httpx
import urllib.parse
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn

app = FastAPI()

# --- CONFIGURATION ---
# Render dashboard mein 'SIXFINGER_KEY' zaroor check karein
SIXFINGER_KEY = os.environ.get("SIXFINGER_KEY", "")
# New Stable API URL
SIXFINGER_URL = "https://api.sixfinger.xyz/v1/chat/completions"

# --- UI DESIGN (Premium Glassmorphism) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>OmniAI - Sixfinger Pro</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background: #020617; color: white; font-family: sans-serif; overflow: hidden; height: 100vh; }
        .glass { background: rgba(15, 23, 42, 0.7); backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.1); }
        .chat-container { height: calc(100vh - 180px); overflow-y: auto; scroll-behavior: smooth; }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 10px; }
    </style>
</head>
<body class="flex items-center justify-center p-4">
    <div class="glass w-full max-w-2xl rounded-[2.5rem] p-6 flex flex-col h-[95vh]">
        <header class="text-center mb-4">
            <h1 class="text-3xl font-extrabold">Omni<span class="text-blue-500">AI</span></h1>
            <p class="text-slate-500 text-xs">Engine: Sixfinger | Status: <span class="text-emerald-500">Online</span></p>
        </header>

        <div id="output" class="chat-container space-y-4 mb-4 flex flex-col-reverse"></div>

        <div class="relative mt-auto">
            <input type="text" id="userInput" placeholder="Ask or command anything..." 
                class="w-full bg-slate-950/50 border border-slate-800 rounded-2xl py-4 px-6 pr-24 outline-none focus:border-blue-500 transition-all text-white">
            <button onclick="processInput()" id="sendBtn" 
                class="absolute right-2 top-2 bottom-2 bg-blue-600 px-6 rounded-xl font-bold hover:bg-blue-500 transition-all">Run</button>
        </div>
    </div>

    <script>
        async function processInput() {
            const input = document.getElementById('userInput');
            const output = document.getElementById('output');
            const btn = document.getElementById('sendBtn');
            const prompt = input.value.trim();
            if(!prompt) return;

            input.value = '';
            btn.disabled = true;
            btn.innerText = "...";

            const formData = new FormData();
            formData.append('prompt', prompt);

            try {
                const res = await fetch('/ask', { method: 'POST', body: formData });
                const data = await res.json();
                
                const card = document.createElement('div');
                card.className = "p-4 rounded-2xl bg-slate-900/60 border border-slate-800 animate-pulse";
                
                if(data.type === 'image') {
                    card.innerHTML = `<img src="${data.result}" class="w-full rounded-xl" onload="this.parentElement.classList.remove('animate-pulse')">`;
                } else {
                    card.classList.remove('animate-pulse');
                    card.innerHTML = `<p class="text-slate-300 text-sm">${data.result}</p>`;
                }
                output.prepend(card);
            } catch (e) {
                alert("Connection failed. Check API key.");
            } finally {
                btn.disabled = false;
                btn.innerText = "Run";
            }
        }
    </script>
</body>
</html>
"""

# --- BACKEND ---

async def call_ai(prompt):
    if not SIXFINGER_KEY:
        return "Error: Render dashboard mein SIXFINGER_KEY set karein!"
    
    headers = {
        "Authorization": f"Bearer {SIXFINGER_KEY}",
        "Content-Type": "application/json"
    }
    
    # Standard Llama/GPT payload
    payload = {
        "model": "gpt-3.5-turbo", 
        "messages": [{"role": "user", "content": prompt}]
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(SIXFINGER_URL, headers=headers, json=payload, timeout=30.0)
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                return f"API Error: Server ne {response.status_code} response diya. URL ya Key check karein."
    except Exception as e:
        return "Connection failed. Please try again later."

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML_TEMPLATE

@app.post("/ask")
async def handle_request(prompt: str = Form(...)):
    text = prompt.lower()
    img_keywords = ["image", "photo", "banao", "picture", "logo", "wallpaper"]

    if any(word in text for word in img_keywords):
        encoded = urllib.parse.quote(prompt)
        seed = os.urandom(2).hex()
        image_url = f"https://pollinations.ai/p/{encoded}?width=1024&height=1024&nologo=true&seed={seed}"
        return {"type": "image", "result": image_url}
    else:
        res = await call_ai(prompt)
        return {"type": "text", "result": res}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
    
