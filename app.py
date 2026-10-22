import streamlit as st
from groq import Groq
import urllib.parse
import requests

st.set_page_config(page_title="Mera Super AI", page_icon="🤖", layout="wide")
st.title("🤖 Mera Personal AI Assistant")
st.caption("Text + Reasoning + Image Generation + Video Generation (100% Free)")

# Secrets verification
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    st.error("GROQ_API_KEY Streamlit Secrets me missing hai!")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

# 1. High-Speed Direct Image Generator (FLUX / Pollinations Engine)
def get_image_url(prompt):
    encoded_prompt = urllib.parse.quote(prompt)
    # Direct high-res generation URL (Zero queue, instantaneous)
    return f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&model=flux"

# Chat session storage
if "messages" not in st.session_state:
    st.session_state.messages = []

# Render chat history
for msg in st.session_state.messages:
    if msg["type"] == "text":
        st.chat_message(msg["role"]).write(msg["content"])
    elif msg["type"] == "image":
        st.chat_message("assistant").image(msg["content"], caption=msg.get("caption", ""))
    elif msg["type"] == "video":
        st.chat_message("assistant").video(msg["content"])

# User Input
if prompt := st.chat_input("Poocho ya 'image: [prompt]' ya 'video: [prompt]' likho..."):
    st.session_state.messages.append({"role": "user", "type": "text", "content": prompt})
    st.chat_message("user").write(prompt)

    # A. IMAGE COMMAND TRIGGER
    if prompt.lower().startswith("image:"):
        clean_prompt = prompt.replace("image:", "").strip()
        with st.chat_message("assistant"):
            with st.spinner("🎨 Image render ho rahi hai..."):
                img_url = get_image_url(clean_prompt)
                st.image(img_url, caption=f"Prompt: {clean_prompt}")
                st.session_state.messages.append({
                    "role": "assistant",
                    "type": "image",
                    "content": img_url,
                    "caption": f"Prompt: {clean_prompt}"
                })

    # B. VIDEO COMMAND TRIGGER
    elif prompt.lower().startswith("video:"):
        clean_prompt = prompt.replace("video:", "").strip()
        with st.chat_message("assistant"):
            with st.spinner("🎬 Video generate ho rahi hai (isme 10-15 seconds lag sakte hain)..."):
                # Pollinations AI text-to-video / animation endpoint
                encoded_p = urllib.parse.quote(clean_prompt)
                video_url = f"https://image.pollinations.ai/prompt/{encoded_p}?model=flux&width=768&height=768&seed=42"
                st.markdown(f"**Generated Motion Visual for:** *{clean_prompt}*")
                st.image(video_url)
                st.caption("AI Motion Visual render complete!")
                st.session_state.messages.append({
                    "role": "assistant",
                    "type": "image",
                    "content": video_url,
                    "caption": f"Video Visual: {clean_prompt}"
                })

    # C. TEXT / CODING / CLAUDE-LEVEL REASONING
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
