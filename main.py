import os
from google import genai # Nayi library import
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
import urllib.parse

app = FastAPI()

# --- CONFIGURATION ---
GEMINI_KEY = os.environ.get("GEMINI_KEY", "")

# Naya Client Setup
client = None
if GEMINI_KEY:
    client = genai.Client(api_key=GEMINI_KEY)
else:
    print("CRITICAL: GEMINI_KEY is missing!")

# --- BACKEND LOGIC ---
async def call_gemini(prompt):
    if not client:
        return "Error: API Key missing!"
    try:
        # Naya method: models.generate_content
        response = client.models.generate_content(
            model='gemini-1.5-flash', 
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Gemini Error: {str(e)}"

@app.post("/ask")
async def handle_request(prompt: str = Form(...)):
    text = prompt.lower()
    img_keywords = ["image", "photo", "banao", "picture", "drawing", "logo"]

    try:
        if any(word in text for word in img_keywords):
            encoded_prompt = urllib.parse.quote(prompt)
            seed = os.urandom(4).hex()
            image_url = f"https://pollinations.ai/p/{encoded_prompt}?width=1024&height=1024&nologo=true&seed={seed}"
            return {"type": "image", "result": image_url}
        else:
            res = await call_gemini(prompt)
            return {"type": "text", "result": res}
    except Exception as e:
        return {"error": str(e)}

# --- UI (HTML_TEMPLATE wahi rahega jo pehle tha) ---
# ... (Aapka HTML code yahan paste karein) ...

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
    
