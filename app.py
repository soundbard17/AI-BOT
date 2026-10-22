import streamlit as st
from groq import Groq
import requests
import time
import io
import base64
from PIL import Image
import re

st.set_page_config(page_title="Mera Super AI", page_icon="🤖", layout="wide")
st.title("🤖 Mera Personal AI Assistant")
st.caption("100% Free & Unlimited (Zero Watermark, Exact Prompt Match) + Fast Reasoning")

# Secrets check
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    st.error("GROQ_API_KEY Streamlit Secrets me missing hai!")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

# 🌟 100% FREE & UNLIMITED CLUSTER (NO WATERMARK, SDXL ENGINE)
def generate_unlimited_image(prompt_text):
    # Public Anonymous Free Cluster Key (Unlimited)
    HORDE_API_KEY = "0000000000"
    
    submit_url = "https://aihorde.net/api/v2/generate/async"
    headers = {
        "apikey": HORDE_API_KEY,
        "Client-Agent": "MeraAIAssistant:1.0:free"
    }
    
    payload = {
        "prompt": f"{prompt_text} ### bad quality, blurry, watermark, signature, ugly, lowres",
        "params": {
            "sampler_name": "k_euler",
            "cfg_scale": 7.5,
            "height": 512,
            "width": 512,
            "steps": 20
        },
        "models": ["ICBINP - I Can't Believe It's Not Photography", "Stable Diffusion"]
    }
    
    # 1. Job submit karein
    res = requests.post(submit_url, json=payload, headers=headers, timeout=20)
    if res.status_code != 202:
        raise Exception(f"Queue error: {res.text}")
    
    job_id = res.json().get("id")
    check_url = f"https://aihorde.net/api/v2/generate/status/{job_id}"
    
    # 2. Render hone ka wait karein (5-15 seconds)
    for _ in range(30):
        time.sleep(2)
        status_res = requests.get(check_url, headers=headers).json()
        if status_res.get("done"):
            img_data = status_res["generations"][0]["img"]
            # Base64 string decode to Image
            img_bytes = base64.b64decode(img_data)
            return Image.open(io.BytesIO(img_bytes))
            
    raise Exception("Image rendering timeout. Cluster busy, please try again.")

# Chat history setup
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    if msg["type"] == "text":
        st.chat_message(msg["role"]).write(msg["content"])
    elif msg["type"] == "image":
        st.chat_message("assistant").image(msg["content"], caption=msg.get("caption", ""))

# User Input
if prompt := st.chat_input("Poocho ya 'create an image of [something]' likho..."):
    st.session_state.messages.append({"role": "user", "type": "text", "content": prompt})
    st.chat_message("user").write(prompt)

    lower_p = prompt.lower()
    image_patterns = [
        r"^image:\s*",
        r"^create an image of\s*",
        r"^create image of\s*",
        r"^create image\s*",
        r"^generate an image of\s*",
        r"^generate image of\s*",
        r"^generate image\s*",
        r"^draw a picture of\s*",
        r"^draw an image of\s*",
        r"^draw\s*",
        r"^make an image of\s*",
        r"^picture of\s*"
    ]
    
    is_image = any(re.search(pat, lower_p) for pat in image_patterns) or lower_p.startswith("image:")

    # 1. IMAGE GENERATION
    if is_image:
        target_prompt = prompt
        for pat in image_patterns:
            target_prompt = re.sub(pat, "", target_prompt, flags=re.IGNORECASE).strip()
            
        if not target_prompt:
            target_prompt = prompt

        with st.chat_message("assistant"):
            with st.spinner(f"🎨 '{target_prompt}' bina watermark ke render ho raha hai (Zero Cost)..."):
                try:
                    img = generate_unlimited_image(target_prompt)
                    st.image(img, caption=f"Result: {target_prompt}")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "type": "image",
                        "content": img,
                        "caption": f"Result: {target_prompt}"
                    })
                except Exception as e:
                    st.error(f"Error: {e}")

    # 2. TEXT / REASONING / CODING
    else:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                chat_context = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages if m["type"] == "text"]
                try:
                    completion = client.chat.completions.create(
                        model="openai/gpt-oss-20b",
                        messages=chat_context
                    )
                    reply = completion.choices[0].message.content
                    st.write(reply)
                    st.session_state.messages.append({"role": "assistant", "type": "text", "content": reply})
                except Exception as e:
                    st.error(f"Error: {e}")
