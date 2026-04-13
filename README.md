# 🇧🇷 Aurya Chat Frontend

Interface moderna de chatbot para consulta de dados públicos brasileiros.

## 🚀 Executar

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar frontend
streamlit run app.py
```

## 🎯 Funcionalidades

### 📱 **Interface de Chat Real**
- Mensagens em tempo real
- Design moderno de chatbot
- Histórico de conversação
- Timestamps e metadata

### 📋 **Sidebar com Instruções**
- Status da conexão API
- Exemplos de perguntas
- Informações da sessão
- Ações (limpar, nova sessão)

### 🔌 **Conectividade**
- WebSocket em tempo real
- Conexão com API em `localhost:8000`
- Tratamento de erros robusto

### 🇧🇷 **Dados Brasileiros**
- 🎓 **Educação:** INEP, IDEB, ENEM
- 🏥 **Saúde:** DATASUS, SUS, estabelecimentos
- 👥 **Demografia:** IBGE, população, IDH

## 📊 **Como Usar**

1. **Iniciar API:** `uvicorn src.api.main:app`
2. **Iniciar Frontend:** `streamlit run app.py`
3. **Acessar:** http://localhost:8501
4. **Conversar:** Digite perguntas sobre dados brasileiros

## 🛠️ **Configuração**

- **API URL:** `ws://localhost:8000/ws`
- **Timeout:** 30 segundos
- **Porta Frontend:** 8501 (padrão Streamlit)

## 🎨 **Design**

- ✅ Chat real com bolhas de mensagem
- ✅ Sidebar com instruções completas  
- ✅ CSS customizado para aparência moderna
- ✅ Responsivo e profissional