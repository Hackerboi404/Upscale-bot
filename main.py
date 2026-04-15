import os
import httpx
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
import urllib.parse

app = FastAPI()

# --- CONFIGURATION ---
# Render dashboard mein SIXFINGER_KEY set karein
SIXFINGER_KEY = os.environ.get("SIXFINGER_KEY", "")

# Sixfinger API endpoint (based on their setup)
SIXFINGER_URL = "https://pi.pythonanywhere.com/v1/chat/completions"

# --- UI DESIGN (Frontend) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>OmniAI - Sixfinger Powered</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap" rel="stylesheet">
    <style>
        body { 
            background: #020617; 
            color: #f8fafc; 
            font-family: 'Plus Jakarta Sans', sans-serif;
            background-image: radial-gradient(circle at top right, #1e1b4b, transparent), radial-gradient(circle at bottom left, #0f172a, transparent);
            overflow: hidden;
        }
        .glass { 
            background: rgba(15, 23, 42, 0.7); 
            backdrop-filter: blur(20px); 
            border: 1px solid rgba(255,255,255,0.08); 
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        }
        .neon-border:focus { 
            border-color: #38bdf8; 
            box-shadow: 0 0 20px rgba(56, 189, 248, 0.3); 
        }
        .loader { 
            border: 2px solid #334155; 
            border-top: 2px solid #38bdf8; 
            border-radius: 50%; 
            width: 18px; 
            height: 18px; 
            animation: spin 0.8s linear infinite; 
            display: none; 
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        #output-area::-webkit-scrollbar { width: 4px; }
        #output-area::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 10px; }
    </style>
</head>
<body class="min-h-screen flex items-center justify-center p-3 md:p-6">
    <div class="glass w-full max-w-3xl rounded-[2rem] p-5 md:p-8 flex flex-col h-[90vh] transition-all duration-300">
        <header class="text-center mb-6">
            <div class="inline-block px-3 py-1 mb-2 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-bold tracking-widest uppercase">
                Free Tier AI Engine (200 Req/Month)
            </div>
            <h1 class="text-3xl md:text-5xl font-extrabold tracking-tight text-white">Omni<span class="text-blue-500">AI</span></h1>
            <p class="text-slate-500 text-xs md:text-sm mt-1">Sixfinger + Pollinations | Think Mode: <span class="text-emerald-400">Automatic</span></p>
        </header>

        <div id="output-area" class="flex-grow space-y-6 overflow-y-auto px-1 pb-4 flex flex-col-reverse text-sm md:text-base">
            <div class="text-slate-600 text-center text-xs py-10">
                Type "Create a cyberpunk car" or ask any question...
            </div>
        </div>

        <div class="relative mt-4 group">
            <input type="text" id="userInput" 
                placeholder="Ask or command anything..." 
                class="w-full bg-slate-950/50 border border-slate-800 rounded-2xl py-4 md:py-5 px-6 pr-24 outline-none neon-border transition-all text-white placeholder:text-slate-600"
                onkeypress="if(event.key === 'Enter') processInput()">
            
            <button onclick="processInput()" id="sendBtn" 
                class="absolute right-2 top-2 bottom-2 bg-blue-600 hover:bg-blue-500 text-white px-5 rounded-xl font-bold transition-all flex items-center gap-2 shadow-lg shadow-blue-900/20">
                <span id="btnText">Run</span>
                <div class="loader" id="loader"></div>
            </button>
        </div>
        
        <div id="status" class="text-[9px] text-blue-500/60 mt-3 text-center tracking-widest uppercase font-bold opacity-0 transition-opacity">
            Routing to best AI...
        </div>
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
            
            // UI Loading State
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
                card.className = "p-5 rounded-3xl bg-slate-900/40 border border-slate-800/60 backdrop-blur-sm animate-in fade-in slide-in-from-bottom-3 duration-500";
                
                let content = `<p class="text-[10px] font-bold text-slate-600 uppercase tracking-tighter mb-3">User: ${prompt}</p>`;

                if(data.type === 'image') {
                    content += `
                        <div class="relative group overflow-hidden rounded-2xl">
                            <img src="${data.result}" class="w-full h-auto object-cover transform transition-transform group-hover:scale-105" alt="AI Generated" onerror="this.src='https://via.placeholder.com/500?text=Image+Load+Failed'">
                        </div>
                        <p class="text-[10px] font-bold text-emerald-400 uppercase tracking-widest mt-3">Image Engine Active</p>`;
                } else {
                    content += `
                        <p class="text-slate-300 leading-relaxed">${data.result.replace(/\\n/g, '<br>')}</p>
                        <p class="text-[10px] font-bold text-blue-400 uppercase tracking-widest mt-4">Sixfinger Chat Engine Active</p>`;
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

async def call_sixfinger(prompt):
    if not SIXFINGER_KEY:
        return "Error: Render पर SIXFINGER_KEY सेट करें!"
    
    headers = {
        "Authorization": f"Bearer {SIXFINGER_KEY}",
        "Content-Type": "application/json"
    }
    
    # Sixfinger ke documentation ke hisab se model name set karein
    # Most likely 'llama-3-70b-instruct' ya similar chalega
    payload = {
        "model": "llama-3-70b-instruct", 
        "messages": [{"role": "user", "content": prompt}]
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(SIXFINGER_URL, headers=headers, json=payload, timeout=60.0)
            
            if response.status_code == 200:
                result = response.json()
                # standard openai format choices[0].message.content
                return result['choices'][0]['message']['content']
            else:
                return f"Sixfinger API Error: {response.status_code} - {response.text}"
                
    except Exception as e:
        return f"System Error: {str(e)}"

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML_TEMPLATE

@app.post("/ask")
async def handle_request(prompt: str = Form(...)):
    text = prompt.lower()
    
    # Auto-Decision Logic
    image_trigger_words = [
        "image", "photo", "banao", "picture", "drawing", 
        "wallpaper", "art", "logo", "generate", "look like"
    ]
    
    try:
        if any(word in text for word in image_trigger_words):
            # Route to Pollinations (Image) - This will always work
            encoded_prompt = urllib.parse.quote(prompt)
            seed = os.urandom(4).hex() 
            image_url = f"https://pollinations.ai/p/{encoded_prompt}?width=1024&height=1024&nologo=true&seed={seed}"
            return {"type": "image", "result": image_url}
        
        else:
            # Route to Sixfinger (Chat)
            result = await call_sixfinger(prompt)
            return {"type": "text", "result": result}
            
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
    
