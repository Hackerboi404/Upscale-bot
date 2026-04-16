import os
import urllib.parse
import requests
from openai import OpenAI
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

# --- CONFIG ---
# Render dashboard mein ye dono keys set karein
HF_TOKEN = os.environ.get("HF_TOKEN")
DEEPAI_KEY = os.environ.get("DEEPAI_API_KEY")

# Chat Client (Hugging Face) - Model updated to a stable one
chat_client = None
if HF_TOKEN:
    chat_client = OpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=HF_TOKEN,
    )

# --- UI DESIGN ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OmniAI Pro</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background: #020617; color: white; font-family: sans-serif; height: 100vh; overflow: hidden; }
        .glass { background: rgba(15, 23, 42, 0.85); backdrop-filter: blur(25px); border: 1px solid rgba(255,255,255,0.1); }
        .chat-area { height: calc(100vh - 180px); overflow-y: auto; scroll-behavior: smooth; }
        .msg-card { background: rgba(30, 41, 59, 0.6); border: 1px solid rgba(255,255,255,0.05); }
    </style>
</head>
<body class="flex items-center justify-center p-3">
    <div class="glass w-full max-w-2xl rounded-[2.5rem] p-6 flex flex-col h-[95vh]">
        <header class="text-center mb-4">
            <h1 class="text-3xl font-black italic text-blue-500">OmniAI <span class="text-white">PRO</span></h1>
            <p class="text-[9px] text-slate-500 uppercase tracking-widest">DeepAI + HF Hybrid</p>
        </header>
        <div id="chat" class="chat-area pr-2 space-y-4"></div>
        <div class="relative mt-auto pt-4">
            <input type="text" id="userInput" placeholder="Ask anything or 'photo'..." 
                class="w-full bg-slate-900 border border-slate-800 rounded-2xl py-4 px-5 pr-20 outline-none text-white focus:border-blue-500">
            <button onclick="send()" id="sendBtn" class="absolute right-2 top-6 bottom-2 bg-blue-600 px-6 rounded-xl font-bold">Run</button>
        </div>
    </div>
    <script>
        async function send() {
            const input = document.getElementById('userInput');
            const chat = document.getElementById('chat');
            const btn = document.getElementById('sendBtn');
            const text = input.value.trim();
            if(!text) return;
            input.value = ''; btn.disabled = true; btn.innerText = '...';
            const formData = new FormData();
            formData.append('prompt', text);
            try {
                const res = await fetch('/ask', { method: 'POST', body: formData });
                const data = await res.json();
                const div = document.createElement('div');
                div.className = "msg-card p-4 rounded-2xl animate-in fade-in duration-300";
                if(data.type === 'image') {
                    div.innerHTML = `<img src="${data.result}" class="w-full rounded-xl shadow-2xl">`;
                } else {
                    div.innerHTML = `<p class="text-sm text-slate-200">${data.result}</p>`;
                }
                chat.appendChild(div);
                chat.scrollTop = chat.scrollHeight;
            } catch(e) { alert("Execution Failed!"); }
            finally { btn.disabled = false; btn.innerText = 'Run'; }
        }
    </script>
</body>
</html>
"""

# --- BACKEND ---
@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML_TEMPLATE

@app.post("/ask")
async def handle_request(prompt: str = Form(...)):
    user_input = prompt.lower().strip()
    img_keywords = ["image", "photo", "banao", "generate", "create", "pic", "art"]

    try:
        # 1. IMAGE LOGIC (DeepAI)
        if any(word in user_input for word in img_keywords):
            if not DEEPAI_KEY:
                return {"type": "text", "result": "DeepAI Key Missing in Render Env!"}
            
            r = requests.post(
                "https://api.deepai.org/api/text2img",
                data={'text': prompt},
                headers={'api-key': DEEPAI_KEY}
            )
            data = r.json()
            if 'output_url' in data:
                return {"type": "image", "result": data['output_url']}
            else:
                return {"type": "text", "result": f"DeepAI Error: {data.get('err', 'Unknown error')}"}

        # 2. CHAT LOGIC (Hugging Face)
        else:
            if not chat_client:
                return {"type": "text", "result": "HF Token Missing!"}
            
            # Using a very stable model name
            completion = chat_client.chat.completions.create(
                model="meta-llama/Llama-3.1-8b-instruct:free", 
                messages=[{"role": "user", "content": prompt}]
            )
            return {"type": "text", "result": completion.choices[0].message.content}

    except Exception as e:
        return {"type": "text", "result": f"System Error: {str(e)}"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
    
