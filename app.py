import streamlit as st
from groq import Groq
import urllib.parse
import random
import re

st.set_page_config(page_title="Mera Super AI", page_icon="🤖", layout="wide")
st.title("🤖 Mera Personal AI Assistant")
st.caption("Accurate Image Generation (No Watermark, Exact Prompt) + Fast Reasoning")

# Secrets check
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    st.error("GROQ_API_KEY missing in Secrets!")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

# 🌟 ACCURATE IMAGE GENERATOR (EXACT PROMPT MATCH, NO WATERMARK)
def generate_exact_image(user_query):
    # Sirf clean user prompt extract karna bina kisi extra character ke
    clean_text = user_query.strip()
    
    # URL encode karna taaki browser exact prompt bheje
    encoded_prompt = urllib.parse.quote(clean_text)
    seed = random.randint(1000, 999999)
    
    # Direct Turbo Engine with STRICT prompt adherence (No Logo, No Portrait Bias)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&seed={seed}&model=turbo&nologo=true"
    return image_url

# Chat memory
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
    
    # Clean image intent trigger
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

    # 1. IMAGE FLOW
    if is_image:
        target_prompt = prompt
        for pat in image_patterns:
            target_prompt = re.sub(pat, "", target_prompt, flags=re.IGNORECASE).strip()
            
        if not target_prompt:
            target_prompt = prompt  # agar prompt match clean karne ke baad empty ho toh original use karein

        with st.chat_message("assistant"):
            with st.spinner(f"🎨 '{target_prompt}' ki exact image ban rahi hai..."):
                img_url = generate_exact_image(target_prompt)
                st.image(img_url, caption=f"Result: {target_prompt}")
                st.session_state.messages.append({
                    "role": "assistant",
                    "type": "image",
                    "content": img_url,
                    "caption": f"Result: {target_prompt}"
                })

    # 2. TEXT FLOW (Chat / Coding)
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
