import os
import google.generativeai as genai
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
import urllib.parse

app = FastAPI()

# --- CONFIGURATION ---
GEMINI_KEY = os.environ.get("GEMINI_KEY", "")

# --- BACKEND ENGINE ---
async def call_gemini(prompt):
    # Naye accounts ke liye ye paths try karna zaroori hai
    models_to_try = [
        'models/gemini-1.5-flash', 
        'gemini-1.5-flash', 
        'models/gemini-pro'
    ]
    
    if not GEMINI_KEY:
        return "Error: Render Dashboard par GEMINI_KEY set karein!"

    genai.configure(api_key=GEMINI_KEY)
    
    for m_name in models_to_try:
        try:
            model = genai.GenerativeModel(m_name)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Failed with {m_name}: {e}")
            continue # Agla model try karega agar 404 aaya toh
            
    return "AI Engine Error: Please check if your API Key is active in Google AI Studio."

# --- UI & ROUTES ---
@app.post("/ask")
async def handle_request(prompt: str = Form(...)):
    text = prompt.lower()
    img_keywords = ["image", "photo", "banao", "picture", "drawing", "logo", "wallpaper"]

    try:
        if any(word in text for word in img_keywords):
            # Image Logic (Pollinations)
            encoded_prompt = urllib.parse.quote(prompt)
            seed = os.urandom(4).hex()
            image_url = f"https://pollinations.ai/p/{encoded_prompt}?width=1024&height=1024&nologo=true&seed={seed}"
            return {"type": "image", "result": image_url}
        else:
            # Chat Logic (Gemini with Fallback)
            res = await call_gemini(prompt)
            return {"type": "text", "result": res}
    except Exception as e:
        return {"error": str(e)}

# Baki ka HTML_TEMPLATE wahi rakhein jo maine pehle diya tha...
