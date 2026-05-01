import streamlit as st
import asyncio
import websockets
import json
import uuid
import os

st.set_page_config(page_title="Aurya", page_icon="💬", layout="centered")

BACKEND_URL = os.getenv("BACKEND_URL", "ws://aurya-backend-svc:8000")
API_WS_URL = BACKEND_URL + "/ws"
TIMEOUT = 300

# Minimal styling
st.markdown("""
<style>
#MainMenu, footer, header, .stDeployButton {display: none !important;}
</style>
""", unsafe_allow_html=True)

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())


async def query_backend(question: str) -> str:
    uri = f"{API_WS_URL}/{st.session_state.session_id}"
    try:
        async with websockets.connect(uri, close_timeout=TIMEOUT) as ws:
            await ws.send(json.dumps({"input_string": question}))
            resp = json.loads(await asyncio.wait_for(ws.recv(), timeout=TIMEOUT))
            return resp.get("answer", "Sem resposta.")
    except Exception as e:
        return f"Erro: {e}"


# Render chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Prompt input
if prompt := st.chat_input("Pergunte sobre dados públicos brasileiros..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Consultando..."):
            answer = asyncio.run(query_backend(prompt))
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})
