"""
🇧🇷 Aurya - Sistema Text-to-SQL para Consulta de Dados Públicos Brasileiros
"""

import streamlit as st
import streamlit.components.v1 as components
import asyncio
import websockets
import json
import time
from datetime import datetime
from typing import Dict, Any
import uuid
import os
import requests

# ========================
# CONFIGURAÇÃO DA PÁGINA
# ========================
st.set_page_config(
    page_title="Aurya - Consulta de Dados Públicos Brasileiros",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="auto"
)

# ========================
# CONFIGURAÇÕES
# ========================
BACKEND_URL = os.getenv("BACKEND_URL", "ws://back:8000")
API_WS_URL = BACKEND_URL + "/ws"
API_HTTP_URL = BACKEND_URL.replace("ws://", "http://").replace("wss://", "https://")
TIMEOUT = 600

# ========================
# CSS CUSTOMIZADO - PALETA IESB
# ========================
st.markdown("""
<style>
/* Reset e hide Streamlit elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {display: none;}

/* Ocultar labels e bordas padrão do Streamlit */
.stTextInput > label {
    display: none !important;
}

.stTextInput,
.stTextInput > div,
.stTextInput > div > div {
    border: none !important;
    padding: 0 !important;
    background: transparent !important;
    outline: none !important;
    box-shadow: none !important;
}

.stTextInput:focus-within,
.stTextInput:focus-within > div,
.stTextInput:focus-within > div > div {
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
}

[data-testid="stForm"],
form {
    border: none !important;
    padding: 0 !important;
    background: transparent !important;
    outline: none !important;
}

.stFormSubmitButton,
.stFormSubmitButton > label,
.stFormSubmitButton > div {
    border: none !important;
    background: transparent !important;
    outline: none !important;
}

.stFormSubmitButton > label {
    display: none !important;
}

/* Background e container principal */
.main {
    background: #f5f5f5;
    padding: 0 !important;
}

.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* Layout de chat full screen */
.chat-layout {
    display: flex;
    flex-direction: column;
    height: 100vh;
    max-height: 100vh;
}

/* Header minimalista fixo - estilo ChatGPT */
.chat-header {
    background: #f5f5f5;
    padding: 0.5rem 1.5rem;
    border-bottom: none;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.chat-header-left {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.chat-header h1 {
    margin: 0;
    font-size: 1.1rem;
    color: #1f2937;
    font-weight: 600;
}

.header-subtitle {
    display: none; /* Ocultar para deixar mais limpo */
}

/* Badge IESB - mais discreto */
.iesb-badge {
    background: #E30613;
    color: white;
    padding: 0.25rem 0.7rem;
    border-radius: 12px;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.3px;
}

/* Actions container no header */
.header-actions {
    display: flex;
    gap: 0.25rem;
    align-items: center;
}

/* Container de mensagens - scrollable */
.messages-container {
    flex: 1;
    overflow-y: auto;
    padding: 1.5rem 1rem;
    background: #f5f5f5;
    scroll-behavior: smooth;
}

/* Centralizar mensagens em telas grandes */
@media (min-width: 1024px) {
    .messages-container {
        padding: 1.5rem calc((100vw - 900px) / 2);
    }
}

/* Mensagens */
.message-wrapper {
    margin-bottom: 1.5rem;
    animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateY(15px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.message-user {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 1rem;
}

.message-assistant {
    display: flex;
    justify-content: flex-start;
    margin-bottom: 1rem;
}

/* Bolhas de mensagem - estilo ChatGPT */
.bubble-user {
    background: #E30613;
    color: white;
    padding: 0.75rem 1rem;
    border-radius: 18px 18px 4px 18px;
    max-width: 70%;
    font-size: 0.95rem;
    line-height: 1.5;
    box-shadow: 0 1px 2px rgba(0,0,0,0.1);
}

.bubble-assistant {
    background: white;
    color: #374151;
    padding: 0.75rem 1rem;
    border-radius: 18px 18px 18px 4px;
    max-width: 75%;
    font-size: 0.95rem;
    line-height: 1.6;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    border: 1px solid #e5e7eb;
}

/* Estilos para elementos markdown dentro da bolha do assistente */
.bubble-assistant h1 {
    font-size: 1.4rem;
    font-weight: 700;
    color: #1f2937;
    margin-bottom: 0.5rem;
    margin-top: 0;
}

.bubble-assistant h2 {
    font-size: 1.2rem;
    font-weight: 600;
    color: #1f2937;
    margin-bottom: 0.4rem;
    margin-top: 0.8rem;
}

.bubble-assistant h3 {
    font-size: 1.05rem;
    font-weight: 600;
    color: #1f2937;
    margin-bottom: 0.3rem;
    margin-top: 0.6rem;
}

.bubble-assistant p {
    margin-bottom: 0.5rem;
}

.bubble-assistant ul {
    margin-left: 1.2rem;
    margin-bottom: 0.5rem;
}

.bubble-assistant li {
    margin-bottom: 0.2rem;
}

.bubble-assistant strong {
    font-weight: 600;
    color: #1f2937;
}

.bubble-assistant code {
    background: #f3f4f6;
    padding: 0.1rem 0.3rem;
    border-radius: 3px;
    font-family: monospace;
    font-size: 0.9em;
}

.bubble-assistant-header {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    margin-bottom: 0.5rem;
}

.assistant-name {
    color: #E30613;
    font-weight: 600;
    font-size: 0.8rem;
}

.time-badge {
    color: #9ca3af;
    font-size: 0.7rem;
    font-weight: normal;
}

.message-timestamp {
    font-size: 0.7rem;
    color: #9ca3af;
    margin-top: 0.3rem;
    text-align: right;
}

.message-timestamp-left {
    text-align: left;
}

/* SQL Query expandable - ajustar expander do Streamlit */
.stExpander {
    border: none !important;
    background: transparent !important;
    margin-top: 0.5rem;
}

.stExpander summary {
    color: #E30613 !important;
    font-weight: 600 !important;
    font-size: 0.75rem !important;
    padding: 0.3rem 0 !important;
}

.stExpander summary:hover {
    opacity: 0.8;
}

/* Code block styling */
.stCodeBlock {
    margin-top: 0.5rem !important;
}

.stCodeBlock pre {
    font-size: 0.75rem !important;
    background: #1e1e2e !important;
}

/* Container spacing */
div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] {
    margin-bottom: 1.5rem;
}

/* Typing indicator - animação de digitação */
.typing-indicator {
    background: white;
    padding: 0.75rem 1rem;
    border-radius: 18px 18px 18px 4px;
    max-width: 75px;
    border: 1px solid #e5e7eb;
    display: inline-block;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

.typing-dots {
    display: flex;
    align-items: center;
    gap: 0.3rem;
    height: 1rem;
}

.typing-dot {
    width: 8px;
    height: 8px;
    background: #9ca3af;
    border-radius: 50%;
    animation: typing 1.4s infinite;
}

.typing-dot:nth-child(2) {
    animation-delay: 0.2s;
}

.typing-dot:nth-child(3) {
    animation-delay: 0.4s;
}

@keyframes typing {
    0%, 60%, 100% {
        transform: translateY(0);
        opacity: 0.7;
    }
    30% {
        transform: translateY(-10px);
        opacity: 1;
    }
}

/* Input area fixa no bottom - estilo ChatGPT */
.input-area {
    background: #f5f5f5;
    padding: 1rem 1rem 1.5rem 1rem;
    border-top: 1px solid #e5e7eb;
}

.input-wrapper {
    max-width: 90%;
    width: 100%;
    margin: 0 auto;
    position: relative;
}

/* Form container positioning */
[data-testid="stForm"] {
    position: relative;
    width: 100% !important;
}

[data-testid="stForm"] > div {
    width: 100% !important;
}

/* Colunas do form lado a lado */
[data-testid="stForm"] [data-testid="column"] {
    padding: 0 !important;
}

[data-testid="stForm"] > div > div[data-testid="column"] {
    display: flex !important;
    align-items: center !important;
    gap: 0.75rem !important;
}

/* Input ocupa o máximo de espaço */
[data-testid="stForm"] .stTextInput,
[data-testid="stForm"] .stTextInput > div,
[data-testid="stForm"] .stTextInput > div > div,
[data-testid="stForm"] .stTextInput input {
    width: 100% !important;
}

/* Botão mantém tamanho fixo */
[data-testid="stForm"] .stFormSubmitButton {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: auto !important;
}

/* Estilo dos inputs do Streamlit - mais compacto */
.stTextInput > div > div > input {
    border: 1px solid #d1d5db;
    border-radius: 24px;
    padding: 0.75rem 1rem;
    font-size: 0.95rem;
    transition: all 0.2s ease;
    background: white;
    color: #1f2937 !important;
    width: 100% !important;
    box-sizing: border-box !important;
    caret-color: #E30613 !important;
}

.stTextInput > div > div > input:focus {
    border-color: #E30613;
    outline: none;
    box-shadow: 0 0 0 1px #E30613;
}

.stTextInput > div > div > input::placeholder {
    color: #9ca3af;
}

.stTextInput > div > div > input:disabled {
    background: #f9fafb !important;
    color: #9ca3af !important;
    cursor: not-allowed !important;
    opacity: 0.7;
}

/* Botão enviar - circular ao lado do input */
.stFormSubmitButton > button {
    background: #E30613 !important;
    color: white !important;
    border: none !important;
    border-radius: 50% !important;
    width: 42px !important;
    height: 42px !important;
    min-width: 42px !important;
    min-height: 42px !important;
    padding: 0 !important;
    font-size: 1.2rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 2px 4px rgba(227, 6, 19, 0.2) !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}

.stFormSubmitButton > button:hover:not(:disabled) {
    background: #c00510 !important;
    transform: scale(1.05) !important;
    box-shadow: 0 4px 8px rgba(227, 6, 19, 0.3) !important;
}

.stFormSubmitButton > button:active:not(:disabled) {
    transform: scale(0.95) !important;
}

.stFormSubmitButton > button:disabled {
    background: #d1d5db !important;
    cursor: not-allowed !important;
    opacity: 0.5 !important;
}

/* Esconder label do form */
.stFormSubmitButton > button p {
    font-size: 0 !important;
}

.stFormSubmitButton > button::before {
    content: "↑";
    font-size: 1.2rem;
    font-weight: bold;
}

/* Botão reiniciar conversa no header - usar seletor mais específico */
.stButton button[kind="secondary"] {
    background: white !important;
    color: #374151 !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 12px !important;
    padding: 0.75rem 1rem !important;
    font-size: 0.85rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
    font-weight: 500 !important;
}

/* Botão reset específico - no header */
button[data-testid="baseButton-secondary"]:has-text("Reiniciar conversa"),
div[data-testid="column"]:last-child button {
    background: #f5f5f5 !important;
    border: none !important;
}

div[data-testid="column"]:last-child button:hover {
    background: white !important;
    border: 1px solid #E30613 !important;
    color: #E30613 !important;
}

/* Welcome screen */
.welcome-screen {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    padding: 3rem 2rem;
    text-align: center;
}

.welcome-logo {
    font-size: 4rem;
    margin-bottom: 1.5rem;
}

.welcome-title {
    font-size: 2.2rem;
    color: #2c3e50;
    margin-bottom: 0.5rem;
    font-weight: 600;
}

.welcome-subtitle {
    font-size: 1.1rem;
    color: #7f8c8d;
    margin-bottom: 2.5rem;
    max-width: 600px;
}

.welcome-cta {
    font-size: 0.95rem;
    color: #95a5a6;
    margin-top: 2rem;
}

.welcome-cta strong {
    color: #E30613;
}

/* Example buttons styling - padronizar todos (exceto form e header) */
.welcome-screen + * .stButton > button,
div[data-testid="column"]:not(:nth-child(2)) .stButton > button {
    background: white !important;
    color: #374151 !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 12px !important;
    padding: 0.75rem 1rem !important;
    font-size: 0.85rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
    font-weight: 500 !important;
    width: 100% !important;
    text-align: left !important;
}

.welcome-screen + * .stButton > button:hover,
div[data-testid="column"]:not(:nth-child(2)) .stButton > button:hover {
    border-color: #E30613 !important;
    color: #E30613 !important;
    background: #fff5f5 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 2px 4px rgba(227, 6, 19, 0.1) !important;
}

/* Scrollbar */
.messages-container::-webkit-scrollbar {
    width: 8px;
}

.messages-container::-webkit-scrollbar-track {
    background: #ecf0f1;
}

.messages-container::-webkit-scrollbar-thumb {
    background: #E30613;
    border-radius: 10px;
}

.messages-container::-webkit-scrollbar-thumb:hover {
    background: #c00510;
}

/* Loading spinner */
.stSpinner > div {
    border-top-color: #E30613 !important;
}

/* Sidebar styling */
section[data-testid="stSidebar"] {
    background: white !important;
    border-right: 1px solid #e5e7eb !important;
    min-width: 400px !important;
    max-width: 400px !important;
    width: 400px !important;
}

section[data-testid="stSidebar"] > div {
    padding: 0.5rem 1rem 1.5rem 1rem !important;
}

/* Logo na sidebar */
section[data-testid="stSidebar"] img {
    border-radius: 8px;
    margin: 0 auto;
    display: block;
}

/* Força texto escuro na sidebar */
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] li,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div {
    color: #374151 !important;
}

section[data-testid="stSidebar"] strong {
    color: #1f2937 !important;
}

/* Sidebar headers */
.sidebar-header {
    color: #E30613 !important;
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
    margin-top: 1rem;
}

.sidebar-subheader {
    color: #374151 !important;
    font-size: 0.9rem;
    font-weight: 600;
    margin-top: 1rem;
    margin-bottom: 0.3rem;
}

/* Expanders na sidebar */
section[data-testid="stSidebar"] .streamlit-expanderHeader {
    color: #374151 !important;
    font-weight: 500 !important;
}

section[data-testid="stSidebar"] .stExpander {
    border-color: #e5e7eb !important;
}

/* Responsive */
@media (max-width: 768px) {
    .bubble-user, .bubble-assistant {
        max-width: 85%;
    }

    .welcome-title {
        font-size: 1.8rem;
    }

    .welcome-subtitle {
        font-size: 1rem;
    }
}
</style>
""", unsafe_allow_html=True)

# ========================
# ESTADO DA SESSÃO
# ========================
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'input_key' not in st.session_state:
    st.session_state.input_key = 0

if 'is_processing' not in st.session_state:
    st.session_state.is_processing = False

# ========================
# FUNÇÕES DE CONEXÃO
# ========================
async def send_message_ws(message: str, session_id: str) -> Dict[str, Any]:
    """Envia mensagem via WebSocket para a API"""
    try:
        uri = f"{API_WS_URL}/{session_id}"
        websocket = await asyncio.wait_for(
            websockets.connect(uri),
            timeout=TIMEOUT
        )

        try:
            payload = {"input_string": message}
            await websocket.send(json.dumps(payload))
            response = await asyncio.wait_for(
                websocket.recv(),
                timeout=TIMEOUT
            )
            return json.loads(response)
        finally:
            await websocket.close()

    except asyncio.TimeoutError:
        return {
            "answer": "A consulta excedeu o tempo limite. Tente uma pergunta mais simples.",
            "query": None,
            "error": True
        }
    except ConnectionRefusedError:
        return {
            "answer": "Não foi possível conectar ao servidor. Verifique se a API está rodando.",
            "query": None,
            "error": True
        }
    except Exception as e:
        return {
            "answer": f"Erro: {str(e)}",
            "query": None,
            "error": True
        }

def run_async_send_message(message: str, session_id: str) -> Dict[str, Any]:
    """Wrapper para executar função async"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(send_message_ws(message, session_id))
        loop.close()
        return result
    except Exception as e:
        return {
            "answer": f"Erro ao processar: {str(e)}",
            "query": None,
            "error": True
        }

# ========================
# FUNÇÕES DE INTERFACE
# ========================
def render_sidebar():
    """Renderiza a sidebar com informações detalhadas"""
    with st.sidebar:
        # Logo IESB
        import os
        logo_path = os.path.join(os.path.dirname(__file__), "logo.png")

        if os.path.exists(logo_path):
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.image(logo_path, width=120)
        else:
            # Fallback: mostrar apenas emoji
            st.markdown('<div style="text-align: center; font-size: 2.5rem; margin: 1rem 0;">🎓</div>', unsafe_allow_html=True)

        #st.markdown("""
        #<div style="text-align: center; padding: 0.5rem 0 1rem 0;">
        #    <p style="color: #6b7280; font-size: 0.9rem; margin: 0;">
        #    </p>
        #</div>
        #""", unsafe_allow_html=True)

        #st.markdown("---")

        st.markdown('<p class="sidebar-header">💬 O que é a Aurya?</p>', unsafe_allow_html=True)
        st.markdown("""
        Assistente virtual com **INTELIGÊNCIA ARTIFICIAL** que permite consultar dados públicos brasileiros
        usando **linguagem natural**, sem necessidade de conhecimento técnico em bancos de dados.

        **Objetivo:** Democratizar o acesso a informações públicas para todos os cidadãos.
        """)

        st.markdown('<p class="sidebar-header">🗄️ Fontes de Dados</p>', unsafe_allow_html=True)

        st.markdown('<p class="sidebar-subheader">📊 Sociodemográficos</p>', unsafe_allow_html=True)
        st.markdown("""
        - **Censo 2022 - IBGE**: Instituto Brasileiro de Geografia e Estatística
        - Dados populacionais por idade, gênero e município
        """)

        # Expander para metadados Censo/IBGE
        with st.expander("📋 Dicionário de dados"):
            tab1, tab2, tab3, tab4 = st.tabs(["👥 População", "🏙️ Municípios", "🗺️ Estados", "🌎 Regiões"])

            with tab1:
                st.markdown("**Tabela: Censo_20222_Populacao_Idade_Sexo**")
                st.markdown("""
                Dados populacionais do Censo 2022 por idade, gênero e município.

                **Colunas principais:**
                - `ANO`: Ano do censo (sempre '2022')
                - `CO_MUNICIPIO`: Código do município (7 dígitos)
                - `IDADE`: Idade em anos (0 a 100+)
                - `SEXO`: Gênero ('Homens' ou 'Mulheres')
                - `TOTAL`: Contagem populacional
                """)

            with tab2:
                st.markdown("**Tabela: municipio**")
                st.markdown("""
                Informações de todos os municípios brasileiros.

                **Colunas principais:**
                - `codigo_municipio_dv`: Código do município (chave primária)
                - `nome_municipio`: Nome do município
                - `cd_uf`: Código do estado
                - `municipio_capital`: É capital? ('Sim' ou 'Não')
                - `longitude` / `latitude`: Coordenadas geográficas
                """)

            with tab3:
                st.markdown("**Tabela: unidade_federacao**")
                st.markdown("""
                Informações dos estados brasileiros (UFs).

                **Colunas principais:**
                - `cd_uf`: Código do estado (chave primária)
                - `sigla_uf`: Sigla do estado (ex: 'SP', 'RJ', 'MG')
                - `nome_uf`: Nome completo do estado
                - `cd_regiao`: Código da região (1-5)

                **Estados por região:**
                - **Norte (1)**: RO, AC, AM, RR, PA, AP, TO
                - **Nordeste (2)**: MA, PI, CE, RN, PB, PE, AL, SE, BA
                - **Sudeste (3)**: MG, ES, RJ, SP
                - **Sul (4)**: PR, SC, RS
                - **Centro-Oeste (5)**: MS, MT, GO, DF
                """)

            with tab4:
                st.markdown("**Tabela: regiao**")
                st.markdown("""
                Informações das 5 regiões brasileiras.

                **Colunas principais:**
                - `cd_regiao`: Código da região (1-5)
                - `nome_regiao`: Nome da região

                **Regiões do Brasil:**
                - **1**: Norte
                - **2**: Nordeste
                - **3**: Sudeste
                - **4**: Sul
                - **5**: Centro-Oeste
                """)


        st.markdown('<p class="sidebar-subheader">🏥 Saúde</p>', unsafe_allow_html=True)
        st.markdown("""
        - **DATASUS**: Departamento de Informática do SUS
        - Procedimentos ambulatoriais (2024 a agosto/2025)
        """)

        # Expander para metadados DATASUS
        with st.expander("📋 Dicionário de dados"):
            tab1, tab2 = st.tabs(["🌍 Localização e Tempo", "📊 Tipos de Procedimentos"])

            with tab1:
                st.markdown("**Informações Geográficas:**")
                st.markdown("""
                - Região (Norte, Nordeste, Sudeste, Sul, Centro-Oeste)
                - Estado (sigla e nome completo)
                - Município (nome e código)
                """)

                st.markdown("**Informações Temporais:**")
                st.markdown("""
                - Ano e mês dos procedimentos
                - Agrupamentos: semestre, trimestre, bimestre
                """)

            with tab2:
                st.markdown("""
                Os procedimentos do SUS estão organizados em **9 grupos principais**, e cada grupo possui **subgrupos detalhados** para informações mais específicas.
                """)

                st.markdown("**Grupos de Procedimentos SUS:**")
                st.markdown("""
                **01 - Promoção e Prevenção**

                **02 - Diagnósticos**

                **03 - Tratamentos Clínicos**

                **04 - Cirurgias**

                **05 - Transplantes**

                **06 - Medicamentos**

                **07 - Órteses, Próteses e Materiais Especiais**

                **08 - Ações Complementares**

                **09 - Atendimentos Integrados**
                """)

        st.markdown('<p class="sidebar-header">💡 Como Usar</p>', unsafe_allow_html=True)
        st.markdown("""
        1. Digite sua pergunta em linguagem natural
        2. Para melhores resultados, consulte os **dicionários de dados**
        3. Clique em **Enviar** ou pressione **Enter**
        4. A Aurya irá gerar e executar uma consulta no Big Data do IESB
        5. Você receberá a resposta em texto simples
        6. Opcionalmente, visualize a consulta executada no Big Data realizada pela Aurya
        """)

        st.markdown('<p class="sidebar-header">🧠 Memória Conversacional</p>', unsafe_allow_html=True)
        st.markdown("""
        A Aurya lembra das suas perguntas anteriores! Você pode fazer perguntas de acompanhamento:

        **Exemplo:**
        - **Você:** "Quantos procedimentos ambulatoriais foram realizados no SUS em 2024?"
        - **Aurya:** *[responde com o total]*
        - **Você:** "E em 2025?"
        - **Aurya:** *[entende que você quer saber sobre procedimentos em 2025]*

        💡 Use o botão "🔄 Reiniciar conversa" para começar uma nova conversa.
        """)

        st.markdown('<p class="sidebar-header">📝 Exemplos</p>', unsafe_allow_html=True)

        with st.expander("📊 Sociodemográficos"):
            st.markdown("""
            - Quais são os 20 municípios mais populosos do Brasil em 2022?
            - Qual a diferença entre a população masculina e feminina no Brasil?
            - Qual a população de 0 a 5 anos (primeira infância) por região em 2022?
            """)

        with st.expander("🏥 Saúde"):
            st.markdown("""
            - Quantos procedimentos ambulatoriais foram realizados no SUS em 2024?
            - Qual o custo médio por atendimento de procedimento ambulatorial no ano de 2024?
            - Quantos exames de ultrassom foram realizados por estado em 2024?
            """)


def render_header():
    """Renderiza o header compacto"""
    col1, col2 = st.columns([4, 1])

    with col1:
        # Header vazio ou com espaçamento mínimo
        st.markdown('<div style="padding: 0.5rem 0;"></div>', unsafe_allow_html=True)

    with col2:
        if st.button("🔄 Reiniciar conversa", key="reset_chat", use_container_width=True):
            # Limpar histórico no backend
            try:
                response = requests.post(
                    f"{API_HTTP_URL}/reset_history/",
                    json={"session_id": st.session_state.session_id},
                    timeout=5
                )
                if response.status_code == 200:
                    print(f"[Frontend] History cleared on backend for session: {st.session_state.session_id}")
            except Exception as e:
                print(f"[Frontend] Error clearing backend history: {e}")

            # Limpar histórico no frontend
            st.session_state.messages = []
            st.session_state.input_key += 1
            st.rerun()

def render_welcome():
    """Renderiza tela de boas-vindas minimalista"""
    st.markdown("""
    <div class="welcome-screen">
        <h1 class="welcome-title">Bem-vindo(a) à Aurya</h1>
        <p class="welcome-subtitle">
            Consulte dados públicos brasileiros em linguagem natural.<br>
            Dados sociodemográficos (IBGE) e de saúde (DATASUS).
        </p>
        <p class="welcome-cta">
            <strong>Digite sua pergunta abaixo</strong> para começar
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Exemplos como botões Streamlit nativos (mais confiável)
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)

    examples = [
        "Qual era a população do Brasil em 2022?",
        "Quantos procedimentos ambulatoriais foram realizados no SUS em 2024?",
        "Qual era a população do Distrito Federal em 2022?"
    ]

    with col1:
        if st.button(f"💡 {examples[0]}", key="ex_1", use_container_width=True):
            st.session_state.pending_message = examples[0]
            st.rerun()

    with col2:
        if st.button(f"💡 {examples[1]}", key="ex_2", use_container_width=True):
            st.session_state.pending_message = examples[1]
            st.rerun()

    with col3:
        if st.button(f"💡 {examples[2]}", key="ex_3", use_container_width=True):
            st.session_state.pending_message = examples[2]
            st.rerun()

def render_typing_indicator():
    """Renderiza indicador de digitação animado"""
    st.markdown("""
    <div class="message-wrapper">
        <div class="message-assistant">
            <div class="typing-indicator">
                <div class="typing-dots">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_messages():
    """Renderiza as mensagens do chat"""
    for msg in st.session_state.messages:
        timestamp = msg["timestamp"].strftime("%H:%M")

        if msg["role"] == "user":
            st.markdown(f"""
            <div class="message-wrapper">
                <div class="message-user">
                    <div>
                        <div style="color: #E30613; font-weight: 600; font-size: 0.8rem; margin-bottom: 0.4rem; text-align: right;">
                            Você
                        </div>
                        <div class="bubble-user">
                            {msg["content"]}
                        </div>
                        <div class="message-timestamp">{timestamp}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        elif msg["role"] == "assistant":
            time_info = msg.get("metadata", {}).get("total_time", "")

            # Usar coluna para alinhar à esquerda
            col1, col2 = st.columns([3, 1])
            with col1:
                # Container com estilo de balão aplicado via CSS inline e markdown
                # Header fora do balão
                if time_info:
                    st.markdown(f'<div style="color: #E30613; font-weight: 600; font-size: 0.8rem; margin-bottom: 0.4rem;">Aurya • {time_info}s</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div style="color: #E30613; font-weight: 600; font-size: 0.8rem; margin-bottom: 0.4rem;">Aurya</div>', unsafe_allow_html=True)

                # Balão branco: usar st.markdown() com markdown content direto
                st.markdown(f"""
                <div style="background: white; padding: 1rem; border-radius: 18px 18px 18px 4px; box-shadow: 0 1px 2px rgba(0,0,0,0.08); border: 1px solid #e5e7eb; margin-bottom: 0.5rem;">

{msg["content"]}

</div>
                """, unsafe_allow_html=True)

                # Timestamp
                st.caption(timestamp)

            # SQL Query como expander nativo do Streamlit
            if msg.get("metadata", {}).get("query"):
                with st.expander("🔍 Ver SQL Query"):
                    st.code(msg["metadata"]["query"], language="sql")

        elif msg["role"] == "error":
            with st.container():
                cols = st.columns([3, 1])
                with cols[0]:
                    st.markdown(f"""
                    <div class="bubble-assistant" style="border-color: #e74c3c;">
                        <div style="color: #e74c3c; font-weight: 600; font-size: 0.8rem; margin-bottom: 0.4rem;">
                            ❌ Erro
                        </div>
                        <div>{msg["content"]}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown(f'<div class="message-timestamp message-timestamp-left">{timestamp}</div>', unsafe_allow_html=True)

    # Âncora invisível no final das mensagens
    st.markdown('<div id="end-of-messages"></div>', unsafe_allow_html=True)

    # Força scroll para o final usando componente HTML com JavaScript
    # Este método é mais confiável pois o componente é carregado após todo o conteúdo
    components.html(
        """
        <script>
            // Aguarda um momento para garantir que todo o DOM foi carregado
            setTimeout(function() {
                // Tenta acessar a janela pai (onde o Streamlit está)
                if (window.parent) {
                    window.parent.document.getElementById('end-of-messages')?.scrollIntoView({behavior: 'smooth', block: 'end'});
                }
            }, 100);
        </script>
        """,
        height=0,
    )

def add_message(role: str, content: str, metadata: Dict = None):
    """Adiciona mensagem ao histórico"""
    st.session_state.messages.append({
        "role": role,
        "content": content,
        "timestamp": datetime.now(),
        "metadata": metadata or {}
    })

def process_user_message(message: str):
    """Processa mensagem do usuário"""
    if not message or not message.strip():
        return

    # Adiciona mensagem do usuário
    add_message("user", message)

    # Marca que está processando para mostrar indicador
    st.session_state.is_processing = True
    st.rerun()

# ========================
# INTERFACE PRINCIPAL
# ========================
def main():
    # Sidebar
    render_sidebar()

    # Header
    render_header()

    # Área de mensagens
    if not st.session_state.messages:
        render_welcome()
    else:
        render_messages()

        # Mostrar indicador de digitação se estiver processando
        if st.session_state.get('is_processing', False):
            render_typing_indicator()

    # Input area - estilo ChatGPT
    st.markdown('<div class="input-area"><div class="input-wrapper">', unsafe_allow_html=True)

    # Bloquear input se estiver processando
    is_processing = st.session_state.get('is_processing', False)

    with st.form(key=f"chat_form_{st.session_state.input_key}", clear_on_submit=True):
        col1, col2 = st.columns([30, 1])

        with col1:
            user_input = st.text_input(
                "Digite sua pergunta:",
                placeholder="Processando..." if is_processing else "Digite sua pergunta...",
                label_visibility="collapsed",
                key=f"input_{st.session_state.input_key}",
                disabled=is_processing
            )

        with col2:
            submit = st.form_submit_button("↑", use_container_width=True, disabled=is_processing)

    st.markdown('</div></div>', unsafe_allow_html=True)

    # Aviso sobre IA Generativa - discreto e elegante
    st.markdown("""
    <div style="
        padding: 0.5rem 1rem;
        margin: 0.5rem 0;
        background-color: #f9fafb;
        border-radius: 4px;
        font-size: 0.85rem;
        color: #6b7280;
        text-align: center;
    ">
        A Aurya pode cometer erros. Sempre verifique as informações fornecidas.
    </div>
    """, unsafe_allow_html=True)

    # Processa mensagem que está em processamento
    if st.session_state.get('is_processing', False):
        # Pega a última mensagem do usuário
        last_user_msg = [msg for msg in st.session_state.messages if msg["role"] == "user"][-1]["content"]

        # Envia para API
        response = run_async_send_message(last_user_msg, st.session_state.session_id)

        # Remove flag de processamento
        st.session_state.is_processing = False

        # Processa resposta
        if response.get("error"):
            add_message("error", response.get("answer", "Erro desconhecido"))
        else:
            metadata = {
                "total_time": response.get("total_time"),
                "query": response.get("query")
            }
            add_message("assistant", response.get("answer", "Sem resposta"), metadata)

        st.rerun()

    # Processa mensagem pendente
    if 'pending_message' in st.session_state:
        msg = st.session_state.pending_message
        del st.session_state.pending_message
        process_user_message(msg)

    # Processa envio do form
    if submit and user_input:
        process_user_message(user_input)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"Erro na aplicação: {str(e)}")
