import streamlit as st
import asyncio
import websockets
import json
import uuid
import os
import re

st.set_page_config(page_title="Aurya", page_icon="💬", layout="centered")

BACKEND_URL = os.getenv("BACKEND_URL", "ws://aurya-backend-svc:8000")
API_WS_URL = BACKEND_URL + "/ws"
TIMEOUT = 300

# Enhanced styling
st.markdown("""
<style>
#MainMenu, footer, header, .stDeployButton {display: none !important;}

.aurya-card {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    border: 1px solid #0f3460;
    border-radius: 12px;
    padding: 1.5rem;
    margin: 0.75rem 0;
    color: #e0e0e0;
}
.aurya-card h3 {
    color: #00d4ff;
    margin: 0 0 0.75rem 0;
    font-size: 1.1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.aurya-metric {
    background: linear-gradient(135deg, #0f3460 0%, #1a1a4e 100%);
    border: 1px solid #00d4ff33;
    border-radius: 10px;
    padding: 1.25rem;
    margin: 0.75rem 0;
    text-align: center;
}
.aurya-metric .value {
    font-size: 2rem;
    font-weight: 700;
    color: #00d4ff;
    letter-spacing: 0.5px;
}
.aurya-metric .label {
    font-size: 0.85rem;
    color: #8892b0;
    margin-top: 0.25rem;
}
.aurya-detail {
    background: #16213e;
    border-left: 3px solid #00d4ff;
    border-radius: 0 8px 8px 0;
    padding: 1rem 1.25rem;
    margin: 0.75rem 0;
    color: #ccd6f6;
    font-size: 0.95rem;
    line-height: 1.6;
}
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


def enhance_output(text: str) -> str:
    """Detect structured data patterns and wrap them in styled HTML cards."""
    lines = text.strip().split("\n")
    if not lines:
        return text

    # Extract title from first H1/H2
    title = ""
    title_idx = -1
    for i, line in enumerate(lines):
        m = re.match(r'^#{1,2}\s+(.+)', line)
        if m:
            title = m.group(1).strip()
            title_idx = i
            break

    # Find the big bold number (metric) — handles **number** or **number text**
    metric_value = ""
    metric_label = ""
    metric_idx = -1
    for i, line in enumerate(lines):
        m = re.search(r'\*\*([0-9][0-9.,]+)\s*(.*?)\*\*', line)
        if m:
            metric_value = m.group(1)
            inner_label = m.group(2).strip()
            outer = re.sub(r'\*\*[^*]+\*\*', '', line).strip().strip(',').strip('.').strip()
            metric_label = inner_label or outer
            metric_idx = i
            break

    # If no structured data detected, return as-is
    if not title and not metric_value:
        return text

    # Collect remaining detail lines
    skip = {title_idx, metric_idx}
    detail_lines = [l for i, l in enumerate(lines) if i not in skip and l.strip()]
    detail_text = "<br>".join(
        re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', l.strip()) for l in detail_lines
    )

    # Build enhanced HTML
    parts = []
    if title:
        icon = "🏥" if any(k in title.lower() for k in ["sus", "saúde", "saude"]) else \
               "🎓" if any(k in title.lower() for k in ["educa", "inep", "enem", "ideb"]) else \
               "👥" if any(k in title.lower() for k in ["popul", "demog", "ibge", "idh"]) else "📊"
        parts.append(f'<div class="aurya-card"><h3>{icon} {title}</h3></div>')

    if metric_value:
        parts.append(
            f'<div class="aurya-metric">'
            f'<div class="value">{metric_value}</div>'
            f'<div class="label">{metric_label}</div>'
            f'</div>'
        )

    if detail_text:
        parts.append(f'<div class="aurya-detail">{detail_text}</div>')

    return "\n".join(parts)


def render_message(role: str, content: str):
    """Render a message, applying enhancement for assistant responses."""
    with st.chat_message(role):
        if role == "assistant":
            enhanced = enhance_output(content)
            if enhanced != content:
                st.html(enhanced)
            else:
                st.markdown(content)
        else:
            st.markdown(content)


# Render chat history
for msg in st.session_state.messages:
    render_message(msg["role"], msg["content"])

# Prompt input
if prompt := st.chat_input("Pergunte sobre dados públicos brasileiros..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Consultando..."):
            answer = asyncio.run(query_backend(prompt))
        enhanced = enhance_output(answer)
        if enhanced != answer:
            st.html(enhanced)
        else:
            st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})
