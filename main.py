import os
import io
import base64
from openai import OpenAI
from huggingface_hub import InferenceClient
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

# --- CONFIG ---
HF_TOKEN = os.environ.get("HF_TOKEN")

# Chat Client (Hugging Face Router)
chat_client = None
if HF_TOKEN:
    chat_client = OpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=HF_TOKEN,
    )

# Image Client (Inference Client)
image_client = None
if HF_TOKEN:
    image_client = InferenceClient(provider="fal-ai", api_key=HF_TOKEN)

# --- UI DESIGN ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
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
            <h1 class="text-3xl font-black italic tracking-tighter text-blue-500">OmniAI <span class="text-white">PRO</span></h1>
            <p class="text-[9px] text-slate-500 uppercase">FAL-AI + ERNIE-IMAGE ENGINE</p>
        </header>

        <div id="chat" class="chat-area pr-2 space-y-4"></div>

        <div class="relative mt-auto pt-4">
            <input type="text" id="userInput" placeholder="Ask or command image..." 
                class="w-full bg-slate-900 border border-slate-800 rounded-2xl py-4 px-5 pr-20 outline-none text-white focus:border-blue-500 transition-all">
            <button onclick="send()" id="sendBtn" class="absolute right-2 top-6 bottom-2 bg-blue-600 px-6 rounded-xl font-bold active:scale-95 transition-all">Run</button>
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
                div.className = "msg-card p-4 rounded-2xl animate-in fade-in duration-500";
                
                if(data.type === 'image') {
                    // Image base64 data dikhane ke liye
                    div.innerHTML = `<img src="data:image/png;base64,${data.result}" class="w-full rounded-xl shadow-2xl">`;
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
    text = prompt.lower()
    img_keywords = ["image", "photo", "banao", "generate", "create", "pic", "art"]

    try:
        if any(word in text for word in img_keywords):
            if not image_client: return {"type": "text", "result": "HF_TOKEN Missing!"}
            
            # Image generation (Binary result)
            image_bytes = image_client.text_to_image(prompt, model="baidu/ERNIE-Image")
            
            # Image ko Base64 string mein badalna taaki frontend par dikh sake
            buffered = io.BytesIO()
            image_bytes.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            return {"type": "image", "result": img_base64}
        
        else:
            # Normal Chat Logic
            if not chat_client: return {"type": "text", "result": "Token Missing!"}
            completion = chat_client.chat.completions.create(
                model="MiniMaxAI/MiniMax-M2.7:together",
                messages=[{"role": "user", "content": prompt}]
            )
            return {"type": "text", "result": completion.choices[0].message.content}

    except Exception as e:
        return {"type": "text", "result": f"Error: {str(e)}"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
    
