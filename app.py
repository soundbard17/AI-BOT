import streamlit as st
from groq import Groq
import urllib.parse
import random

st.set_page_config(page_title="Mera Super AI", page_icon="🤖", layout="wide")
st.title("🤖 Mera Personal AI Assistant")
st.caption("Clean HD Image Generation (No Watermark, 100% Free) + Claude-level Reasoning")

# Secrets check
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    st.error("GROQ_API_KEY Streamlit Secrets me missing hai!")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

# 🌟 ZERO-WATERMARK HIGH-RES ENGINE
def generate_clean_hd_image(prompt):
    # Professional photorealistic enhancers
    enhancers = "photorealistic, 8k resolution, raw photo, master studio lighting, sharp focus, highly detailed, high quality, uncompressed"
    full_prompt = f"{prompt}, {enhancers}"
    encoded = urllib.parse.quote(full_prompt)
    seed = random.randint(10000, 999999)
    
    # Direct pure visual generation (Watermark disabled, turbo crisp render)
    image_url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&seed={seed}&model=flux&nologo=true&private=true&enhance=false"
    return image_url

# Chat session memory
if "messages" not in st.session_state:
    st.session_state.messages = []

# Messages render
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
            with st.spinner("🎨 Clean HD Image render ho rahi hai (Bina Watermark)..."):
                try:
                    img_url = generate_clean_hd_image(clean_prompt)
                    st.image(img_url, caption=f"✨ HD Render: {clean_prompt}")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "type": "image",
                        "content": img_url,
                        "caption": f"✨ HD Render: {clean_prompt}"
                    })
                except Exception as e:
                    st.error(f"Image error: {e}")

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
