import os
from google import genai
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import uvicorn
import urllib.parse

app = FastAPI()

# --- CONFIGURATION ---
GEMINI_KEY = os.environ.get("GEMINI_KEY", "")

# Client initialization
client = None
if GEMINI_KEY:
    client = genai.Client(api_key=GEMINI_KEY)

# --- UI DESIGN ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OmniAI - Smart Router</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background: #020617; color: white; font-family: sans-serif; }
        .glass { background: rgba(15, 23, 42, 0.9); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1); }
    </style>
</head>
<body class="min-h-screen flex items-center justify-center p-4">
    <div class="glass w-full max-w-2xl rounded-[2rem] p-6 md:p-10 shadow-2xl text-center">
        <h1 class="text-4xl font-bold mb-6 text-white">Omni<span class="text-blue-500">AI</span></h1>
        
        <div id="output" class="mb-6 space-y-4 text-left max-h-[300px] overflow-y-auto px-2"></div>

        <div class="relative">
            <input type="text" id="userInput" placeholder="Kuch bhi pucho ya photo banao..." 
                class="w-full bg-slate-900 border border-slate-800 rounded-xl p-4 outline-none focus:border-blue-500">
            <button onclick="send()" class="absolute right-2 top-2 bottom-2 bg-blue-600 px-4 rounded-lg font-bold">Run</button>
        </div>
    </div>

    <script>
        async function send() {
            const input = document.getElementById('userInput');
            const output = document.getElementById('output');
            const prompt = input.value;
            if(!prompt) return;
            
            input.value = '';
            const formData = new FormData();
            formData.append('prompt', prompt);

            const res = await fetch('/ask', { method: 'POST', body: formData });
            const data = await res.json();
            
            const div = document.createElement('div');
            div.className = "p-4 bg-slate-800 rounded-xl border border-slate-700";
            
            if(data.type === 'image') {
                div.innerHTML = `<img src="${data.result}" class="w-full rounded-lg">`;
            } else {
                div.innerHTML = `<p>${data.result}</p>`;
            }
            output.prepend(div);
        }
    </script>
</body>
</html>
"""

# --- ROUTES ---

@app.get("/", response_class=HTMLResponse)
async def home():
    # Ye home page load karega jab aap URL open karenge
    return HTML_TEMPLATE

@app.post("/ask")
async def handle_request(prompt: str = Form(...)):
    text = prompt.lower()
    img_keywords = ["photo", "image", "banao", "picture", "art"]

    try:
        if any(word in text for word in img_keywords):
            # Image Generator (Pollinations)
            encoded = urllib.parse.quote(prompt)
            image_url = f"https://pollinations.ai/p/{encoded}?width=1024&height=1024&nologo=true&seed={os.urandom(2).hex()}"
            return {"type": "image", "result": image_url}
        else:
            # Chat Generator (Gemini New Library)
            if not client:
                return {"type": "text", "result": "Error: API Key missing!"}
            
            response = client.models.generate_content(
                model='gemini-1.5-flash', 
                contents=prompt
            )
            return {"type": "text", "result": response.text}
    except Exception as e:
        return {"type": "text", "result": f"Error: {str(e)}"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
    
