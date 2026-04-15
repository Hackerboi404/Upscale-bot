import os
import google.generativeai as genai
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn

app = FastAPI()

# --- CONFIGURATION ---
# Render ke Environment Variables se key lega, agar nahi mili toh placeholder
GEMINI_KEY = os.environ.get("GEMINI_KEY", "YOUR_GEMINI_FREE_API_KEY")
genai.configure(api_key=GEMINI_KEY)
chat_model = genai.GenerativeModel('gemini-1.5-flash')

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
        body { 
            background: #020617; 
            color: #f8fafc; 
            font-family: 'Plus Jakarta Sans', sans-serif;
            background-image: radial-gradient(circle at top right, #1e1b4b, transparent), radial-gradient(circle at bottom left, #0f172a, transparent);
        }
        .glass { 
            background: rgba(15, 23, 42, 0.8); 
            backdrop-filter: blur(16px); 
            border: 1px solid rgba(255,255,255,0.1); 
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
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-thumb { background: #334155; border-radius: 10px; }
    </style>
</head>
<body class="min-h-screen flex items-center justify-center p-4">
    <div class="glass w-full max-w-2xl rounded-[2.5rem] p-6 md:p-10 transition-all">
        <header class="text-center mb-10">
            <div class="inline-block px-4 py-1.5 mb-4 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-bold tracking-widest uppercase">
                Zero-Choice AI Orchestrator
            </div>
            <h1 class="text-5xl font-extrabold tracking-tight text-white mb-2">Omni<span class="text-blue-500">AI</span></h1>
            <p class="text-slate-400 font-medium">Think Mode: <span class="text-emerald-400">Automatic</span></p>
        </header>

        <div id="output-area" class="space-y-6 mb-8 max-h-[450px] overflow-y-auto px-2 pb-4 flex flex-col-reverse">
            <div class="text-slate-500 text-center text-sm py-10">
                Type "Create a 3D neon logo" or ask any question...
            </div>
        </div>

        <div class="relative group">
            <input type="text" id="userInput" 
                placeholder="Ask or command anything..." 
                class="w-full bg-slate-950/50 border border-slate-800 rounded-2xl py-5 px-6 pr-28 outline-none neon-border transition-all text-white placeholder:text-slate-600"
                onkeypress="if(event.key === 'Enter') processInput()">
            
            <button onclick="processInput()" id="sendBtn" 
                class="absolute right-2 top-2 bottom-2 bg-blue-600 hover:bg-blue-500 text-white px-6 rounded-xl font-bold transition-all flex items-center gap-2 group shadow-lg shadow-blue-900/20">
                <span id="btnText">Run</span>
                <div class="loader" id="loader"></div>
            </button>
        </div>
        
        <div id="status" class="text-[10px] text-blue-500/60 mt-4 text-center tracking-widest uppercase font-bold opacity-0 transition-opacity">
            System Routing to best AI...
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
                
                const card = document.createElement('div');
                card.className = "p-5 rounded-3xl bg-slate-900/50 border border-slate-800/50 backdrop-blur-sm animate-in fade-in slide-in-from-bottom-4 duration-500";
                
                let content = `<p class="text-[10px] font-bold text-slate-500 uppercase tracking-tighter mb-3">Prompt: ${prompt}</p>`;

                if(data.type === 'image') {
                    content += `
                        <div class="relative group overflow-hidden rounded-2xl">
                            <img src="${data.result}" class="w-full h-auto object-cover transform transition-transform group-hover:scale-105" alt="AI Generated">
                        </div>
                        <div class="mt-3 flex items-center gap-2">
                            <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                            <p class="text-xs font-bold text-emerald-400 uppercase tracking-widest">Image Engine Active</p>
                        </div>`;
                } else {
                    content += `
                        <p class="text-slate-300 leading-relaxed text-sm md:text-base">${data.result.replace(/\\n/g, '<br>')}</p>
                        <div class="mt-4 flex items-center gap-2">
                            <span class="w-2 h-2 rounded-full bg-blue-500"></span>
                            <p class="text-xs font-bold text-blue-400 uppercase tracking-widest">Reasoning Engine Active</p>
                        </div>`;
                }
                
                card.innerHTML = content;
                output.prepend(card);
            } catch (err) {
                console.error(err);
                alert("Connection failed. Check your API key.");
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

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML_TEMPLATE

@app.post("/ask")
async def handle_request(prompt: str = Form(...)):
    text = prompt.lower()
    
    # Auto-Decision Logic (Image vs Chat)
    image_trigger_words = [
        "image", "photo", "banao", "picture", "drawing", 
        "wallpaper", "art", "logo", "sketch", "generate", "look like"
    ]
    
    try:
        if any(word in text for word in image_trigger_words):
            # Route to Pollinations (Flux model used via 'model' param)
            seed = os.urandom(4).hex() # To get a fresh image every time
            image_url = f"https://pollinations.ai/p/{prompt.replace(' ', '%20')}?width=1024&height=1024&nologo=true&model=flux&seed={seed}"
            return {"type": "image", "result": image_url}
        
        else:
            # Route to Gemini 1.5 Flash
            response = chat_model.generate_content(prompt)
            return {"type": "text", "result": response.text}
            
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    # Render Dynamic Port Binding
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
    
