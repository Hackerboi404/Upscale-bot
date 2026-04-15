import os
import httpx
import urllib.parse
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

# --- CONFIGURATION (Render Dashboard mein ye keys daalein) ---
# OpenRouter Free models ke liye key yahan se milti hai: https://openrouter.ai/keys
OPENROUTER_KEY = os.environ.get("OPENROUTER_KEY", "")

# --- AI ENGINES ---

async def call_openrouter(prompt):
    if not OPENROUTER_KEY:
        return "Error: Render par OPENROUTER_KEY set karein!"
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "HTTP-Referer": "https://render.com", # Required by OpenRouter
        "Content-Type": "application/json"
    }
    
    # Hum 'free' model use karenge jo hamesha chalta hai
    payload = {
        "model": "google/gemini-2.0-flash-exp:free", 
        "messages": [{"role": "user", "content": prompt}]
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload, timeout=20.0)
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            else:
                return f"OpenRouter Error: {response.status_code}. Key check karein."
    except Exception as e:
        return "Connection failed. Please try again."

# --- UI DESIGN (Wahi Premium Glassmorphism) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>OmniAI - G4F Style</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background: #020617; color: white; font-family: sans-serif; overflow: hidden; height: 100vh; }
        .glass { background: rgba(15, 23, 42, 0.75); backdrop-filter: blur(25px); border: 1px solid rgba(255,255,255,0.1); }
        .chat-area { height: calc(100vh - 200px); overflow-y: auto; }
        .user-msg { background: #1e293b; border-radius: 1.5rem 1.5rem 0 1.5rem; }
        .ai-msg { background: rgba(56, 189, 248, 0.1); border: 1px solid rgba(56, 189, 248, 0.2); border-radius: 1.5rem 1.5rem 1.5rem 0; }
    </style>
</head>
<body class="flex items-center justify-center p-2 md:p-6">
    <div class="glass w-full max-w-2xl rounded-[2.5rem] p-5 md:p-8 flex flex-col h-[95vh]">
        <header class="text-center mb-4">
            <h1 class="text-3xl font-black tracking-tighter">Omni<span class="text-blue-500">AI</span></h1>
            <p class="text-[10px] text-slate-500 uppercase tracking-widest">Multi-Provider Orchestrator</p>
        </header>

        <div id="chat" class="chat-area space-y-4 mb-4 pr-2">
            <div class="ai-msg p-4 text-sm text-slate-300">Hello! Main kaise madad kar sakta hoon?</div>
        </div>

        <div class="relative mt-auto">
            <input type="text" id="userInput" placeholder="Ask anything..." 
                class="w-full bg-slate-900/50 border border-slate-800 rounded-2xl py-4 px-5 pr-20 outline-none focus:border-blue-500 transition-all">
            <button onclick="send()" id="sendBtn" class="absolute right-2 top-2 bottom-2 bg-blue-600 px-5 rounded-xl font-bold">Run</button>
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
            btn.innerText = '...';

            const formData = new FormData();
            formData.append('prompt', text);

            try {
                const res = await fetch('/ask', { method: 'POST', body: formData });
                const data = await res.json();
                
                const div = document.createElement('div');
                if(data.type === 'image') {
                    div.className = "ai-msg p-2";
                    div.innerHTML = `<img src="${data.result}" class="w-full rounded-xl">`;
                } else {
                    div.className = "ai-msg p-4 text-sm";
                    div.innerText = data.result;
                }
                chat.appendChild(div);
                chat.scrollTop = chat.scrollHeight;
            } catch(e) {
                alert("Error connecting to server.");
            } finally {
                btn.innerText = 'Run';
            }
        }
    </script>
</body>
</html>
"""

# --- ROUTES ---

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML_TEMPLATE

@app.post("/ask")
async def handle_request(prompt: str = Form(...)):
    query = prompt.lower()
    img_keywords = ["image", "photo", "banao", "picture", "logo"]

    if any(word in query for word in img_keywords):
        encoded = urllib.parse.quote(prompt)
        # Seed change karne se har baar nayi photo aayegi
        url = f"https://pollinations.ai/p/{encoded}?width=1024&height=1024&nologo=true&seed={os.urandom(2).hex()}"
        return {"type": "image", "result": url}
    else:
        res = await call_openrouter(prompt)
        return {"type": "text", "result": res}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
    
