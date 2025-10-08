# --- Importações Essenciais ---
import streamlit as st
import base64
import os

def welcome_screen():
    """Exibe a tela de boas-vindas com um design aprimorado e moderno."""

    # CSS para estilizar os cartões e a página
    st.markdown("""
    <style>
    .card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 25px 20px;
        text-align: center;
        box-shadow: 0 4px 8px 0 rgba(0,0,0,0.1);
        transition: 0.3s;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: start;
    }
    .card:hover {
        box-shadow: 0 8px 16px 0 rgba(0,0,0,0.2);
    }
    .card h5 {
        color: #495057;
        font-size: 1.2rem;
        margin-bottom: 15px;
    }
    .card p {
        color: #6c757d;
        text-align: left;
        font-size: 0.95rem;
    }
    .stButton>button {
        font-size: 1.1rem;
        padding: 10px 24px;
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- Seção Hero ---
    with st.container():
        # Logo
        logo_path = "asset/LOGO.png"
        if os.path.exists(logo_path):
            with open(logo_path, "rb") as f:
                data = base64.b64encode(f.read()).decode("utf-8")
            st.markdown(
                f"<div style='text-align: center; padding-bottom: 20px;'><img src='data:image/png;base64,{data}' width='300'></div>",
                unsafe_allow_html=True
            )
        
        st.markdown("<h1 style='text-align: center; color: #2c3e50;'>First Class Agent EDA</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; color: #34495e; margin-bottom: 30px;'>Sua plataforma de elite para Análise Exploratória de Dados</h3>", unsafe_allow_html=True)

        # Botão de Ação
        _ , btn_col, _ = st.columns([2.5, 1.5, 2.5])
        with btn_col:
            if st.button("🚀 Iniciar Análise", use_container_width=True, type="primary"):
                st.session_state.welcome_seen = True
                st.rerun()

    st.markdown("--- ")

    # --- Seção de Funcionalidades ---
    st.markdown("<h2 style='text-align: center; color: #2c3e50; margin-bottom: 30px;'>Funcionalidades Principais</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="card">
            <div style='font-size: 4rem;'>🧠</div>
            <h5>Análise Inteligente</h5>
            <p>Faça perguntas em linguagem natural e receba análises complexas, desde estatísticas descritivas a correlações e insights proativos.</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="card">
            <div style='font-size: 4rem;'>📊</div>
            <h5>Visualização Dinâmica</h5>
            <p>Gere automaticamente gráficos, como histogramas e diagramas de barras, para visualizar seus dados de forma clara e informativa.</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="card">
            <div style='font-size: 4rem;'>✨</div>
            <h5>Powered by Gemini</h5>
            <p>Utiliza o poder dos modelos de IA mais avançados do Google para garantir insights precisos, relevantes e contextualizados.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("--- ")

    # --- Como Começar ---
    st.markdown("<h2 style='text-align: center; color: #2c3e50; margin-bottom: 30px;'>Como Começar</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="card">
            <div style='font-size: 3.5rem; color: #0d6efd; font-weight: 600;'>1 🔑</div>
            <h5 style="margin-top: 15px;">Autenticação</h5>
            <p>Na próxima tela, insira sua chave de API do Google Gemini para ativar o agente de análise.</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="card">
            <div style='font-size: 3.5rem; color: #0d6efd; font-weight: 600;'>2 📤</div>
            <h5 style="margin-top: 15px;">Upload do CSV</h5>
            <p>Na barra lateral da aplicação, carregue o arquivo de dados no formato CSV que você deseja analisar.</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="card">
            <div style='font-size: 3.5rem; color: #0d6efd; font-weight: 600;'>3 💬</div>
            <h5 style="margin-top: 15px;">Análise Interativa</h5>
            <p>Converse com o agente de IA através do chat para fazer perguntas e gerar visualizações sobre seus dados.</p>
        </div>
        """, unsafe_allow_html=True)

    # --- Rodapé ---
    st.markdown("<p style='text-align: center; color: #7f8c8d; padding-top: 30px;'>Uma solução moderna para análise de dados inteligente.</p>", unsafe_allow_html=True)