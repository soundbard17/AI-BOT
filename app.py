import streamlit as st
from groq import Groq
import requests
import io
from PIL import Image

st.set_page_config(page_title="Mera Super AI", page_icon="🤖", layout="wide")
st.title("🤖 Mera Personal AI Assistant")
st.caption("Official FLUX.1 Engine (No Watermark, Ultra-HD) + Claude-level Reasoning")

# Secrets check
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
HF_TOKEN = st.secrets.get("HF_TOKEN")

if not GROQ_API_KEY or not HF_TOKEN:
    st.error("GROQ_API_KEY ya HF_TOKEN Streamlit Secrets me missing hai!")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

# 🌟 DIRECT FLUX.1 ENGINE (NO WATERMARK, HIGH QUALITY)
def generate_flux_image(prompt):
    # Black Forest Labs official FLUX.1-schnell via Hugging Face router
    API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    # Prompt enhancement for photorealism
    enhanced_prompt = f"{prompt}, 8k, photorealistic, cinematic lighting, sharp focus, masterpiece, highly detailed"
    payload = {
        "inputs": enhanced_prompt,
        "parameters": {"num_inference_steps": 4}
    }
    
    response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
    
    if response.status_code == 200:
        return Image.open(io.BytesIO(response.content))
    else:
        # Fallback to SDXL agar router busy ho
        FALLBACK_URL = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"
        fb_res = requests.post(FALLBACK_URL, headers=headers, json={"inputs": enhanced_prompt}, timeout=60)
        if fb_res.status_code == 200:
            return Image.open(io.BytesIO(fb_res.content))
        raise Exception(f"API Error ({response.status_code}): {response.text}")

# Chat history setup
if "messages" not in st.session_state:
    st.session_state.messages = []

# Purane messages render karein
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
    image_keywords = ["image:", "create image", "create an image", "generate image", "generate an image", "draw", "picture of"]
    is_image = any(k in lower_p for k in image_keywords)

    # 1. IMAGE GENERATION
    if is_image:
        clean_prompt = prompt
        for k in ["image:", "create an image of", "create image of", "create image", "generate an image of", "generate image of", "generate image", "draw a picture of", "draw", "picture of"]:
            clean_prompt = clean_prompt.lower().replace(k, "").strip()

        with st.chat_message("assistant"):
            with st.spinner("🎨 FLUX.1 Engine se High-Res Image ban rahi hai (Zero Watermark)..."):
                try:
                    img = generate_flux_image(clean_prompt)
                    st.image(img, caption=f"✨ FLUX HD: {clean_prompt}")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "type": "image",
                        "content": img,
                        "caption": f"✨ FLUX HD: {clean_prompt}"
                    })
                except Exception as e:
                    st.error(f"Image generation me error aaya: {e}")

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
