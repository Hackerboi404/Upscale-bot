import os
import urllib.parse
from openai import OpenAI
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

# --- CONFIG ---
# Together AI ya Hugging Face Router Key yahan daalein
API_KEY = os.environ.get("HF_TOKEN") # Ya TOGETHER_KEY

client = None
if API_KEY:
    client = OpenAI(
        base_url="https://router.huggingface.co/v1", # Hugging Face Router
        api_key=API_KEY,
    )

# --- UI DESIGN ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OmniAI - Fixed</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background: #020617; color: white; font-family: sans-serif; height: 100vh; overflow: hidden; }
        .glass { background: rgba(15, 23, 42, 0.8); backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.1); }
        .chat-area { height: calc(100vh - 180px); overflow-y: auto; }
        .msg-card { background: rgba(30, 41, 59, 0.5); border: 1px solid rgba(255,255,255,0.05); }
    </style>
</head>
<body class="flex items-center justify-center p-3">
    <div class="glass w-full max-w-2xl rounded-[2.5rem] p-6 flex flex-col h-[95vh]">
        <header class="text-center mb-4">
            <h1 class="text-3xl font-black italic text-blue-500">Omni<span class="text-white">AI</span></h1>
            <p class="text-[9px] text-slate-500">STRICT HYBRID MODE</p>
        </header>

        <div id="chat" class="chat-area pr-2 space-y-4"></div>

        <div class="relative mt-auto">
            <input type="text" id="userInput" placeholder="Kuch bhi pucho ya 'photo' maango..." 
                class="w-full bg-slate-950 border border-slate-800 rounded-2xl py-4 px-5 pr-20 outline-none text-white focus:border-blue-500">
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

            input.value = ''; btn.disabled = true; btn.innerText = '...';

            const formData = new FormData();
            formData.append('prompt', text);

            try {
                const res = await fetch('/ask', { method: 'POST', body: formData });
                const data = await res.json();
                
                const div = document.createElement('div');
                div.className = "msg-card p-4 rounded-2xl animate-in fade-in duration-300";
                
                if(data.type === 'image') {
                    div.innerHTML = `<img src="${data.result}" class="w-full rounded-xl" loading="lazy">`;
                } else {
                    div.innerHTML = `<p class="text-sm text-slate-200">${data.result}</p>`;
                }
                chat.appendChild(div);
                chat.scrollTop = chat.scrollHeight;
            } catch(e) { console.error(e); }
            finally { btn.disabled = false; btn.innerText = 'Run'; }
        }
    </script>
</body>
</html>
"""

# --- BACKEND ---
@app.post("/ask")
async def handle_request(prompt: str = Form(...)):
    user_input = prompt.lower().strip()
    
    # Ye keywords decide karenge ki chat karni hai ya photo
    img_keywords = ["image", "photo", "banao", "generate", "create", "pic", "art", "drawing"]
    
    # 1. PEHLE CHECK KARO: Kya user image chahta hai?
    if any(word in user_input for word in img_keywords):
        # Agar image maangi hai, toh Hugging Face Chat ko call hi nahi karenge
        safe_prompt = urllib.parse.quote(prompt)
        seed = os.urandom(2).hex()
        # Pollinations is best for now because it's FREE and NO-LIMIT
        image_url = f"https://pollinations.ai/p/{safe_prompt}?width=1024&height=1024&seed={seed}&nologo=true"
        return {"type": "image", "result": image_url}
    
    # 2. AGAR IMAGE NAHI HAI: Tab chat trigger karo
    else:
        try:
            if not client: return {"type": "text", "result": "API Key Missing!"}
            
            completion = client.chat.completions.create(
                model="meta-llama/Llama-3-70b-chat-hf", # Stable model
                messages=[{"role": "user", "content": prompt}]
            )
            return {"type": "text", "result": completion.choices[0].message.content}
        except Exception as e:
            return {"type": "text", "result": f"Chat Error: {str(e)}"}

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML_TEMPLATE

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
    
