import streamlit as st
from groq import Groq
import requests

st.set_page_config(page_title="Mera Super AI", page_icon="🤖")
st.title("🤖 Mera Personal AI Assistant")
st.caption("Text + Reasoning + Image Generation")

# Secrets se keys fetch karna
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
HF_TOKEN = st.secrets["HF_TOKEN"]

client = Groq(api_key=GROQ_API_KEY)

def generate_image(prompt):
    API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
    return response.content

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    if msg["type"] == "text":
        st.chat_message(msg["role"]).write(msg["content"])
    elif msg["type"] == "image":
        st.chat_message("assistant").image(msg["content"])

if prompt := st.chat_input("Kuch bhi poocho ya 'image: [prompt]' likho..."):
    st.session_state.messages.append({"role": "user", "type": "text", "content": prompt})
    st.chat_message("user").write(prompt)

    if prompt.lower().startswith("image:"):
        clean_prompt = prompt.replace("image:", "").strip()
        with st.chat_message("assistant"):
            with st.spinner("Image render ho rahi hai..."):
                img_bytes = generate_image(clean_prompt)
                st.image(img_bytes)
                st.session_state.messages.append({"role": "assistant", "type": "image", "content": img_bytes})
    else:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                chat_context = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages if m["type"] == "text"]
                completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=chat_context
                )
                reply = completion.choices[0].message.content
                st.write(reply)
                st.session_state.messages.append({"role": "assistant", "type": "text", "content": reply})
