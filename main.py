import os
import urllib.parse
from openai import OpenAI
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

# --- CONFIGURATION ---
# Code ab seedha Render ke environment se token uthayega
HF_TOKEN = os.environ.get("HF_TOKEN")

# Client setup (Sirf tabhi chalega jab token milega)
client = None
if HF_TOKEN:
    client = OpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=HF_TOKEN,
    )

# --- UI DESIGN ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>OmniAI - Private Engine</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background: #020617; color: white; font-family: sans-serif; overflow: hidden; height: 100vh; }
        .glass { background: rgba(15, 23, 42, 0.75); backdrop-filter: blur(25px); border: 1px solid rgba(255,255,255,0.1); }
        .chat-area { height: calc(100vh - 200px); overflow-y: auto; scroll-behavior: smooth; }
        .msg-bubble { background: rgba(30, 41, 59, 0.6); border: 1px solid rgba(255,255,255,0.05); }
    </style>
</head>
<body class="flex items-center justify-center p-4">
    <div class="glass w-full max-w-2xl rounded-[2.5rem] p-6 flex flex-col h-[95vh]">
        <header class="text-center mb-6">
            <h1 class="text-3xl font-black italic">Omni<span class="text-blue-500">AI</span></h1>
            <p class="text-[10px] text-slate-500 uppercase tracking-widest">Secure HF Router Active</p>
        </header>

        <div id="chat" class="chat-area space-y-4 mb-4 pr-2 text-sm text-slate-300">
            <div class="msg-bubble p-4 rounded-2xl">Setup Complete. Kya help kar sakta hoon?</div>
        </div>

        <div class="relative mt-auto">
            <input type="text" id="userInput" placeholder="Ask anything..." 
                class="w-full bg-slate-950 border border-slate-800 rounded-2xl py-4 px-5 pr-20 outline-none focus:border-blue-500 transition-all">
            <button onclick="send()" id="sendBtn" class="absolute right-2 top-2 bottom-2 bg-blue-600 px-6 rounded-xl font-bold hover:bg-blue-500">Run</button>
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
                div.className = "msg-bubble p-4 rounded-2xl animate-in fade-in duration-300";
                
                if(data.type === 'image') {
                    div.innerHTML = `<img src="${data.result}" class="w-full rounded-xl">`;
                } else {
                    div.innerHTML = `<p>${data.result}</p>`;
                }
                chat.appendChild(div);
                chat.scrollTop = chat.scrollHeight;
            } catch(e) {
                alert("Check if HF_TOKEN is set in Render Dashboard.");
            } finally {
                btn.innerText = 'Run';
            }
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
    text = prompt.lower()
    img_keywords = ["image", "photo", "banao", "picture", "logo"]

    try:
        if any(word in text for word in img_keywords):
            encoded = urllib.parse.quote(prompt)
            image_url = f"https://pollinations.ai/p/{encoded}?width=1024&height=1024&nologo=true&seed={os.urandom(2).hex()}"
            return {"type": "image", "result": image_url}
        else:
            if not client:
                return {"type": "text", "result": "Error: HF_TOKEN missing in environment!"}
            
            completion = client.chat.completions.create(
                model="MiniMaxAI/MiniMax-M2.7:together",
                messages=[{"role": "user", "content": prompt}]
            )
            return {"type": "text", "result": completion.choices[0].message.content}
    except Exception as e:
        return {"type": "text", "result": f"Execution Error: {str(e)}"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
    
