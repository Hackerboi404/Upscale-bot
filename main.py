import os
import google.generativeai as genai
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
import urllib.parse

app = FastAPI()

# --- CONFIGURATION ---
GEMINI_KEY = os.environ.get("GEMINI_KEY", "")

# Initial Setup
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)
else:
    print("CRITICAL: GEMINI_KEY is missing!")

# --- UI DESIGN (Frontend) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OmniAI - Smart Router</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap" rel="stylesheet">
    <style>
        body { background: #020617; color: #f8fafc; font-family: 'Plus Jakarta Sans', sans-serif; background-image: radial-gradient(circle at top right, #1e1b4b, transparent), radial-gradient(circle at bottom left, #0f172a, transparent); }
        .glass { background: rgba(15, 23, 42, 0.8); backdrop-filter: blur(16px); border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5); }
        .neon-border:focus { border-color: #38bdf8; box-shadow: 0 0 20px rgba(56, 189, 248, 0.3); }
        .loader { border: 2px solid #334155; border-top: 2px solid #38bdf8; border-radius: 50%; width: 18px; height: 18px; animation: spin 0.8s linear infinite; display: none; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-thumb { background: #334155; border-radius: 10px; }
    </style>
</head>
<body class="min-h-screen flex items-center justify-center p-4">
    <div class="glass w-full max-w-2xl rounded-[2.5rem] p-6 md:p-10 transition-all">
        <header class="text-center mb-10">
            <div class="inline-block px-4 py-1.5 mb-4 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-bold tracking-widest uppercase">Zero-Choice AI Orchestrator</div>
            <h1 class="text-5xl font-extrabold tracking-tight text-white mb-2">Omni<span class="text-blue-500">AI</span></h1>
            <p class="text-slate-400 font-medium">Think Mode: <span class="text-emerald-400">Automatic</span></p>
        </header>
        <div id="output-area" class="space-y-6 mb-8 max-h-[450px] overflow-y-auto px-2 pb-4 flex flex-col-reverse">
            <div class="text-slate-500 text-center text-sm py-10">Type "Create a 3D neon logo" or ask any question...</div>
        </div>
        <div class="relative group">
            <input type="text" id="userInput" placeholder="Ask or command anything..." class="w-full bg-slate-950/50 border border-slate-800 rounded-2xl py-5 px-6 pr-28 outline-none neon-border transition-all text-white placeholder:text-slate-600" onkeypress="if(event.key === 'Enter') processInput()">
            <button onclick="processInput()" id="sendBtn" class="absolute right-2 top-2 bottom-2 bg-blue-600 hover:bg-blue-500 text-white px-6 rounded-xl font-bold transition-all flex items-center gap-2 group shadow-lg shadow-blue-900/20">
                <span id="btnText">Run</span>
                <div class="loader" id="loader"></div>
            </button>
        </div>
        <div id="status" class="text-[10px] text-blue-500/60 mt-4 text-center tracking-widest uppercase font-bold opacity-0 transition-opacity">System Routing...</div>
    </div>
    <script>
        async function processInput() {
            const input = document.getElementById('userInput');
            const btnText = document.getElementById('btnText');
            const loader = document.getElementById('loader');
            const output = document.getElementById('output-area');
            const status = document.getElementById('status');
            if(!input.value.trim()) return;
            const prompt = input.value;
            input.value = '';
            btnText.style.display = 'none';
            loader.style.display = 'block';
            status.style.opacity = '1';
            const formData = new FormData();
            formData.append('prompt', prompt);
            try {
                const response = await fetch('/ask', { method: 'POST', body: formData });
                const data = await response.json();
                if (data.error) throw new Error(data.error);
                const card = document.createElement('div');
                card.className = "p-5 rounded-3xl bg-slate-900/50 border border-slate-800/50 backdrop-blur-sm mb-4";
                let content = `<p class="text-[10px] font-bold text-slate-500 uppercase tracking-tighter mb-3">Prompt: ${prompt}</p>`;
                if(data.type === 'image') {
                    content += `<div class="relative overflow-hidden rounded-2xl"><img src="${data.result}" class="w-full h-auto" onerror="this.src='https://via.placeholder.com/500?text=Image+Load+Failed'"></div>`;
                } else {
                    content += `<p class="text-slate-300 text-sm md:text-base">${data.result.replace(/\\n/g, '<br>')}</p>`;
                }
                card.innerHTML = content;
                output.prepend(card);
            } catch (err) {
                alert("AI Error: " + err.message);
            } finally {
                btnText.style.display = 'block';
                loader.style.display = 'none';
                status.style.opacity = '0';
            }
        }
    </script>
</body>
</html>
"""

# --- BACKEND LOGIC ---

async def call_gemini(prompt):
    # Try multiple model names to avoid 404
    models_to_try = ['gemini-1.5-flash', 'gemini-1.5-flash-latest', 'gemini-pro']
    last_error = ""
    
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            last_error = str(e)
            continue
    return f"Gemini Error: {last_error}"

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML_TEMPLATE

@app.post("/ask")
async def handle_request(prompt: str = Form(...)):
    text = prompt.lower()
    image_trigger_words = ["image", "photo", "banao", "picture", "drawing", "wallpaper", "logo"]
    
    try:
        if any(word in text for word in image_trigger_words):
            encoded_prompt = urllib.parse.quote(prompt)
            seed = os.urandom(4).hex() 
            image_url = f"https://pollinations.ai/p/{encoded_prompt}?width=1024&height=1024&nologo=true&seed={seed}"
            return {"type": "image", "result": image_url}
        else:
            if not GEMINI_KEY:
                return {"error": "API Key missing in Render Settings!"}
            
            result = await call_gemini(prompt)
            return {"type": "text", "result": result}
            
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
    
