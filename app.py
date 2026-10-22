import streamlit as st
from groq import Groq
import urllib.parse
import random

st.set_page_config(page_title="Mera Super AI", page_icon="🤖", layout="wide")
st.title("🤖 Mera Personal AI Assistant")
st.caption("Ultra-HD Image Engine (FLUX) + Claude-level Reasoning")

# Secrets check
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    st.error("GROQ_API_KEY missing in Secrets!")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

# 🌟 ULTRA-HD IMAGE GENERATOR (FLUX Engine + Auto-Enhance)
def get_high_res_image_url(prompt):
    # Professional photography & rendering boosters
    enhancers = "ultra-realistic, 8k resolution, shot on 35mm lens, f/1.8, cinematic studio lighting, highly detailed textures, photorealistic masterpiece, sharp focus"
    full_prompt = f"{prompt}, {enhancers}"
    encoded = urllib.parse.quote(full_prompt)
    seed = random.randint(1000, 999999)
    # FLUX.1 Pro quality pipeline with enhance=true
    return f"https://image.pollinations.ai/prompt/{encoded}?width=1280&height=1280&seed={seed}&model=flux-realism&nologo=true&enhance=true"

# Chat history
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
    image_keywords = ["image:", "create image", "create an image", "generate image", "generate an image", "draw", "picture of"]
    is_image = any(k in lower_p for k in image_keywords)

    # IMAGE GENERATION
    if is_image:
        clean_prompt = prompt
        for k in ["image:", "create an image of", "create image of", "create image", "generate an image of", "generate image of", "generate image", "draw a picture of", "draw", "picture of"]:
            clean_prompt = clean_prompt.lower().replace(k, "").strip()

        with st.chat_message("assistant"):
            with st.spinner("🎨 Ultra-HD Photorealistic Image render ho rahi hai..."):
                img_url = get_high_res_image_url(clean_prompt)
                st.image(img_url, caption=f"✨ 8K Render: {clean_prompt}")
                st.session_state.messages.append({
                    "role": "assistant",
                    "type": "image",
                    "content": img_url,
                    "caption": f"✨ 8K Render: {clean_prompt}"
                })

    # TEXT / REASONING / CODING
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
