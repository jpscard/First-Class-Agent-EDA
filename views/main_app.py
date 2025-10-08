# --- Importações Essenciais ---
import streamlit as st
import pandas as pd
import os
import uuid
import shutil
import io
from contextlib import redirect_stdout
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from utils import (
    get_gemini_models, 
    parse_agent_thoughts, 
    display_formatted_thoughts,
    export_chat_to_pdf
)

def main_app():
    """A aplicação principal de EDA."""
    plots_dir = "temp_plots"
    if 'uploader_key' not in st.session_state: st.session_state.uploader_key = 0
    
    # --- Carregamento de Modelos ---
    @st.cache_data
    def load_models():
        gemini_models = get_gemini_models()
        return gemini_models
    
    gemini_models = load_models()

    # --- Barra Lateral ---
    with st.sidebar:
        logo_path = "asset/LOGO.png"
        if os.path.exists(logo_path):
            st.image(logo_path, width=200)
        st.header(f"Bem-vindo, {st.session_state['user_name']}!")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Logout", use_container_width=True):
                if os.path.exists(plots_dir):
                    shutil.rmtree(plots_dir)
                st.session_state.clear()
                if "GOOGLE_API_KEY" in os.environ:
                    del os.environ["GOOGLE_API_KEY"]
                st.rerun()
        with col2:
            if st.button("Reiniciar Chat", use_container_width=True):
                if 'messages' in st.session_state:
                    del st.session_state.messages
                if os.path.exists(plots_dir):
                    shutil.rmtree(plots_dir)
                    os.makedirs(plots_dir, exist_ok=True)
                # Incrementa a chave para forçar o reset do file_uploader
                st.session_state.uploader_key += 1
                st.rerun()

        st.divider()
        st.header("Painel de Controle")
        
        selected_model = None
        if gemini_models:
            filtered_gemini_models = [m for m in gemini_models if 'gemini' in m]
            default_model = 'models/gemini-1.5-flash-latest'
            default_index = filtered_gemini_models.index(default_model) if default_model in filtered_gemini_models else 0
            selected_model = st.selectbox("Modelo Gemini:", filtered_gemini_models, index=default_index)
        else:
            st.warning("Nenhum modelo Gemini encontrado.")

        uploaded_file = st.file_uploader("Selecione seu arquivo CSV", type=["csv"], key=f"uploader_{st.session_state.uploader_key}")

        st.divider()

        # Seção de Exportação
        if st.session_state.get("messages"):
            st.subheader("Exportar Análise")
            if st.button("Gerar Relatório em PDF"):
                with st.spinner("O agente está escrevendo o sumário e gerando o PDF..."):
                    # Inicializa o LLM para ser usado na criação do sumário
                    llm = None
                    if selected_model and os.getenv("GOOGLE_API_KEY"):
                        llm = ChatGoogleGenerativeAI(model=selected_model.replace('models/', ''), temperature=0)
                    
                    if llm:
                        pdf_data = export_chat_to_pdf(st.session_state.messages, st.session_state['user_name'], llm)
                        st.session_state['pdf_data'] = pdf_data
                    else:
                        st.error("Não foi possível inicializar o modelo para gerar o sumário.")
            
            if st.session_state.get('pdf_data') is not None:
                st.download_button(
                    label="Baixar PDF",
                    data=st.session_state.get('pdf_data'),
                    file_name=f"relatorio_eda_{st.session_state.get('current_file', 'analise').split('.')[0]}.pdf",
                    mime="application/pdf"
                )

        st.divider()
        show_thoughts = st.toggle("Modo Desenvolvedor (Ver Pensamentos)", value=False)

    # --- Interface Principal ---
    if uploaded_file is not None:
        # Limpa o histórico e plots se um novo arquivo for carregado
        if st.session_state.get("current_file") != uploaded_file.name:
            if os.path.exists(plots_dir):
                shutil.rmtree(plots_dir)
            os.makedirs(plots_dir, exist_ok=True)
            st.session_state.messages = []
            st.session_state.current_file = uploaded_file.name
        try:
            df = pd.read_csv(uploaded_file)
            st.success("Arquivo carregado com sucesso! Amostra dos dados:")
            st.dataframe(df.head())
            if "messages" not in st.session_state: st.session_state.messages = []

            # Exibe histórico
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
                    if "images" in message:
                        for img_path in message["images"]:
                            if os.path.exists(img_path):
                                st.image(img_path)
                    if message.get("role") == "assistant" and "thoughts" in message:
                        with st.expander("Ver pensamentos do Agente 🧠"):
                            if isinstance(message["thoughts"], list):
                                display_formatted_thoughts(message["thoughts"])
                            else:
                                st.code(message["thoughts"], language='text')
            
            # Input do usuário
            if prompt := st.chat_input("Converse com seus dados..."):
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)

                # --- Lógica de Triagem ---
                simple_greetings = ["oi", "olá", "ola", "tudo bem?", "tudo bem", "eai", "e ai"]
                normalized_prompt = prompt.lower().strip("?!., ")

                if normalized_prompt in simple_greetings:
                    # Resposta simples para saudações
                    response = "Olá! Sou seu assistente de análise. Como posso ajudar com seus dados hoje?"
                    assistant_message = {"role": "assistant", "content": response}
                    st.session_state.messages.append(assistant_message)
                    with st.chat_message("assistant"):
                        st.markdown(response)
                else:
                    # Apenas para perguntas reais, aciona o agente
                    llm = None
                    if selected_model and os.getenv("GOOGLE_API_KEY"):
                        llm = ChatGoogleGenerativeAI(model=selected_model.replace('models/', ''), temperature=0)
                    else:
                        st.error("Por favor, selecione um modelo Gemini e verifique se a chave de API está configurada.")
                    
                    if llm:
                        with st.spinner("O agente está pensando..."):
                            agent = create_pandas_dataframe_agent(llm, df, agent_type="zero-shot-react-description", verbose=True, allow_dangerous_code=True, handle_parsing_errors=True)
                            try:
                                # --- PROMPT ENGINEERING ---
                                system_prompt = f"""
Você é um assistente de IA especialista em Análise Exploratória de Dados (EDA). Sua missão é ser um parceiro analítico para o usuário.

**FORMATO DE SAÍDA OBRIGATÓRIO:**
Sua resposta DEVE SEMPRE começar com "Thought:" e terminar com o bloco "Final Answer:". Toda a sua resposta final para o usuário deve estar contida nele. NUNCA dê a resposta final sem o prefixo "Final Answer:".

**Sua Diretriz Principal: Adapte-se ao usuário.**

1.  **Para Saudações Simples (oi, olá, etc.):** Se o usuário apenas cumprimentar, responda de forma breve e amigável (ex: "Olá! Como posso ajudar com seus dados hoje?") e aguarde o comando dele. Não inicie uma análise completa.

2.  **Para Pedidos de Análise:** Quando o usuário pedir uma análise, siga a estrutura abaixo:
    a. **Primeiro, atenda:** Entregue o resultado direto (texto ou gráfico) que foi solicitado.
    b. **Depois, guie:** Após entregar o resultado, agregue valor:
        - **Explique:** Diga o que o resultado significa.
        - **Observe:** Compartilhe qualquer insight proativo que você encontrou.
        - **Sugira:** Recomende um próximo passo lógico para a análise.
        - **Engaje:** Termine com uma pergunta para manter a conversa fluindo.

**Outras Diretrizes Importantes:**
- **Idioma:** Responda sempre no idioma da pergunta do usuário.
- **Melhores Práticas:** Crie gráficos com títulos e rótulos claros.
- **Gráficos:** Use `matplotlib` ou `seaborn`. **CRÍTICO: Salve sempre o gráfico em `plot.png`**. Não use `plt.show()`.
"""
                                recent_messages = st.session_state.messages[-10:]
                                history = "\n".join([f" - {m['role']}: {m['content']}" for m in recent_messages])
                                full_prompt = f"{system_prompt}\n\n**Contexto da Conversa Anterior:**\n{history}\n\n**Pergunta do Usuário:**\n{prompt}"

                                # Garante que não há um plot antigo poluindo a pasta raiz
                                if os.path.exists("plot.png"):
                                    os.remove("plot.png")

                                # 1. Snapshot dos arquivos antes da execução
                                files_before = set(os.listdir("."))

                                # Executa o agente
                                response_dict = agent.invoke({"input": full_prompt})
                                response = response_dict.get('output', 'Não foi possível obter uma resposta.')
                                
                                agent_thoughts_raw = ""
                                if show_thoughts:
                                    string_io = io.StringIO()
                                    with redirect_stdout(string_io):
                                        agent.invoke({"input": full_prompt})
                                    agent_thoughts_raw = string_io.getvalue()

                                # 2. Snapshot após execução e identifica novos arquivos
                                files_after = set(os.listdir("."))
                                new_files = files_after - files_before
                                
                                assistant_message = {"role": "assistant", "content": response}
                                if agent_thoughts_raw:
                                    assistant_message["thoughts"] = parse_agent_thoughts(agent_thoughts_raw)

                                # 3. Processa e move todos os novos arquivos de imagem
                                new_image_paths = []
                                for filename in new_files:
                                    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                                        if not os.path.exists(plots_dir):
                                            os.makedirs(plots_dir, exist_ok=True)
                                        
                                        old_path = os.path.join(".", filename)
                                        # Gera um nome de arquivo único para evitar conflitos
                                        unique_filename = f"{uuid.uuid4()}.png"
                                        new_path = os.path.join(plots_dir, unique_filename)
                                        os.rename(old_path, new_path)
                                        new_image_paths.append(new_path)

                                # Adiciona as imagens à mensagem e as exibe
                                if new_image_paths:
                                    assistant_message["images"] = new_image_paths # Armazena como lista

                                with st.chat_message("assistant"):
                                    st.markdown(response)
                                    if "images" in assistant_message:
                                        for img_path in assistant_message["images"]:
                                            st.image(img_path)
                                    
                                    if "thoughts" in assistant_message and assistant_message["thoughts"]:
                                        with st.expander("Ver pensamentos do Agente 🧠"):
                                            display_formatted_thoughts(assistant_message["thoughts"])
                                
                                st.session_state.messages.append(assistant_message)

                            except Exception as e:
                                st.error(f"Ocorreu um erro ao executar o agente: {e}")
        except Exception as e:
            st.error(f"Ocorreu um erro ao carregar o arquivo CSV: {e}")
    else:
        st.markdown("---")
        st.markdown("<h2 style='text-align: center;'>Plataforma Pronta para Análise</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>Para começar, carregue um arquivo CSV usando o painel à sua esquerda.</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        st.subheader("Exemplos de Perguntas")
        col1, col2 = st.columns(2)
        with col1:
            st.info("📄 **Análise Descritiva**\n- 'Faça um resumo estatístico dos dados.'\n- 'Quais são os tipos de dados de cada coluna?'\n- 'Existem valores ausentes?'")
        with col2:
            st.info("📊 **Visualização e Gráficos**\n- 'Crie um histograma da coluna idade.'\n- 'Mostre a correlação entre as colunas X e Y.'\n- 'Gere um gráfico de barras para a coluna de categorias.'")
        
        st.warning("**Modo Desenvolvedor:** Ative o 'Modo Desenvolvedor' no painel de controle para visualizar o processo de raciocínio do agente em tempo real.")
