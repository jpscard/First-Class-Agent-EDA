# --- Importações Essenciais ---
import streamlit as st
import os
import base64
from utils import validate_gemini_api_key

def login_page():
    """Exibe a página de login em um layout centralizado."""
    _, col, _ = st.columns([1, 2, 1])
    with col:
        logo_path = "asset\LOGO.png"
        if os.path.exists(logo_path):
            with open(logo_path, "rb") as f:
                data = base64.b64encode(f.read()).decode("utf-8")
            st.markdown(f"<div style='text-align: center'><img src='data:image/png;base64,{data}' width='300'></div>", unsafe_allow_html=True)
                
        name = st.text_input("Seu Nome", key="login_name")
        password = st.text_input("Insira sua API Key do Gemini", type="password", key="login_password")
        
        if st.button("Login", use_container_width=True, type="primary"):
            if name and password:
                with st.spinner("Validando sua chave de API..."):
                    is_valid = validate_gemini_api_key(password)
                
                if is_valid:
                    st.session_state["logged_in"] = True
                    st.session_state["user_name"] = name
                    os.environ["GOOGLE_API_KEY"] = password
                    st.success("Login bem-sucedido!")
                    st.rerun()
                # Se a chave não for válida, a função validate_gemini_api_key já exibe o st.error.
                # Nenhuma ação adicional é necessária aqui.
            else:
                st.error("Por favor, insira seu nome e a API Key.")