# --- Importações Essenciais ---
import streamlit as st
import re
import google.generativeai as genai
from google.api_core import exceptions
from fpdf import FPDF
import os
from datetime import datetime

# --- Classe para PDF com Cabeçalho e Rodapé ---
class PDF(FPDF):
    def header(self):
        if os.path.exists("asset/LOGO.png"):
            self.image("asset/LOGO.png", 10, 8, 25)
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Relatório de Análise de Dados', 0, 1, 'C')
        
        # Adiciona Autor e Data
        if hasattr(self, 'author') and hasattr(self, 'generation_date'):
            self.set_font('Arial', '', 9)
            self.cell(0, 5, f"Autor: {self.author}", 0, 1, 'R')
            self.cell(0, 5, f"Gerado em: {self.generation_date}", 0, 1, 'R')

        self.ln(5) # Espaço reduzido após o cabeçalho

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

# --- Função de Geração de PDF ---
def export_chat_to_pdf(messages, user_name, llm):
    """Gera um relatório em PDF a partir do histórico de mensagens, incluindo um sumário executivo."""
    
    # 1. Gerar o Sumário Executivo com o LLM
    summary_text = ""
    try:
        conversation_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
        summary_prompt = f"""
Você é um analista de dados sênior. Sua tarefa é ler o histórico de uma conversa entre um usuário e um agente de IA sobre uma análise de dados e escrever um sumário executivo conciso em português (2 a 3 parágrafos). 
O sumário deve destacar as principais perguntas feitas, as análises realizadas e os insights ou conclusões mais importantes encontrados. Ignore saudações e foque nos resultados.

Histórico da Conversa:
---
{conversation_history}
---

Sumário Executivo:"""
        
        response = llm.invoke(summary_prompt)
        summary_text = response.content
    except Exception as e:
        summary_text = f"Ocorreu um erro ao gerar o sumário executivo: {e}"

    # 2. Gerar o PDF
    pdf = PDF()
    pdf.author = user_name
    pdf.generation_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    pdf.add_page()
    
    # Adiciona fontes que suportam caracteres Unicode, com fallback para Arial
    try:
        pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
        pdf.set_font('DejaVu', '', 10)
        font_family = 'DejaVu'
    except Exception:
        st.warning("Fonte DejaVuSans.ttf não encontrada. Usando Arial como alternativa. Caracteres especiais podem não ser exibidos corretamente.")
        pdf.set_font('Arial', '', 10)
        font_family = 'Arial'

    # Adiciona o Sumário Executivo
    pdf.set_font(font_family, 'B' if font_family == 'Arial' else '', 12)
    pdf.cell(0, 10, 'Sumário Executivo', 0, 1, 'L')
    pdf.set_font(font_family, '', 10)
    pdf.multi_cell(0, 5, summary_text)
    pdf.add_page() # Nova página para o histórico detalhado

    pdf.set_fill_color(240, 240, 240)
    
    # Adiciona o histórico completo da conversa
    pdf.set_font(font_family, 'B' if font_family == 'Arial' else '', 12)
    pdf.cell(0, 10, 'Histórico Detalhado da Análise', 0, 1, 'L')
    pdf.ln(5)

    for msg in messages:
        is_user = msg["role"] == "user"
        
        # Define o estilo para a mensagem
        pdf.set_font(font_family, 'B' if is_user and font_family == 'Arial' else '', 11)
        pdf.set_text_color(0, 0, 0)
        
        # Cabeçalho da mensagem (Usuário ou Agente)
        actor = user_name if is_user else "Agente de IA"
        pdf.cell(0, 10, actor, 0, 1, 'L')
        
        # Corpo da mensagem
        pdf.set_font(font_family, '', 10)
        pdf.multi_cell(w=0, h=5, text=msg["content"], border=0, align='L', fill=is_user)
        
        # Adiciona imagens se existirem
        if "images" in msg:
            for img_path in msg["images"]:
                if os.path.exists(img_path):
                    pdf.ln(5)
                    # Adiciona a imagem, garantindo que não exceda a largura da página
                    pdf.image(img_path, x=None, y=None, w=pdf.w - 40)
                    pdf.ln(5)
            
        pdf.ln(7) # Espaçamento reduzido entre mensagens

    return bytes(pdf.output(dest='S'))


# --- Funções de Formatação de Pensamentos do Agente ---
def parse_agent_thoughts(thought_string):
    """Analisa a string de saída do agente e a transforma em uma lista estruturada."""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|(?:\\[0-?]*[ -/]*[@-~]))')
    thought_string = ansi_escape.sub('', thought_string)
    if '> Finished chain.' in thought_string:
        thought_string = thought_string.split('> Finished chain.')[0]
    pattern = re.compile(r"(Thought|Action|Action Input|Observation):(.+?)(?=(Thought|Action|Action Input|Observation):|> Entering new AgentExecutor chain.|$)", re.DOTALL)
    matches = pattern.findall(thought_string)
    parsed_steps = []
    for match in matches:
        step_type = match[0].strip()
        content = match[1].strip()
        parsed_steps.append({"type": step_type, "content": content})
    return parsed_steps

def display_formatted_thoughts(parsed_thoughts):
    """Exibe os pensamentos do agente de forma formatada no Streamlit."""
    for i, step in enumerate(parsed_thoughts):
        if step["type"] == "Thought":
            st.markdown(f"🤔 **Pensamento**")
            st.markdown(f"> {step['content'].strip()}")
        elif step["type"] == "Action":
            st.markdown(f"🎬 **Ação:** `{step['content']}`")
        elif step["type"] == "Action Input":
            st.markdown(f"⌨️ **Input da Ação**")
            st.code(step['content'], language='python')
        elif step["type"] == "Observation":
            st.markdown(f"🔍 **Observação**")
            st.text(step['content'])
        if i < len(parsed_thoughts) - 1:
            st.markdown("--- ")

# --- Funções de Validação e Obtenção de Modelos ---
def validate_gemini_api_key(api_key):
    try:
        genai.configure(api_key=api_key)
        genai.list_models()
        return True
    except exceptions.PermissionDenied:
        st.error("Chave de API do Gemini inválida ou sem permissão.")
        return False
    except Exception as e:
        st.error(f"Ocorreu um erro ao validar a chave de API: {e}")
        return False

def get_gemini_models():
    try:
        return [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    except Exception as e:
        st.warning(f"Não foi possível buscar modelos Gemini. Verifique a API Key. Erro: {e}")
        return []

    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|(?:\\[0-?]*[ -/]*[@-~]))')
    thought_string = ansi_escape.sub('', thought_string)
    if '> Finished chain.' in thought_string:
        thought_string = thought_string.split('> Finished chain.')[0]
    pattern = re.compile(r"(Thought|Action|Action Input|Observation):(.+?)(?=(Thought|Action|Action Input|Observation):|> Entering new AgentExecutor chain.|$)", re.DOTALL)
    matches = pattern.findall(thought_string)
    parsed_steps = []
    for match in matches:
        step_type = match[0].strip()
        content = match[1].strip()
        parsed_steps.append({"type": step_type, "content": content})
    return parsed_steps

def display_formatted_thoughts(parsed_thoughts):
    """Exibe os pensamentos do agente de forma formatada no Streamlit."""
    for i, step in enumerate(parsed_thoughts):
        if step["type"] == "Thought":
            st.markdown(f"🤔 **Pensamento**")
            st.markdown(f"> {step['content'].strip()}")
        elif step["type"] == "Action":
            st.markdown(f"🎬 **Ação:** `{step['content']}`")
        elif step["type"] == "Action Input":
            st.markdown(f"⌨️ **Input da Ação**")
            st.code(step['content'], language='python')
        elif step["type"] == "Observation":
            st.markdown(f"🔍 **Observação**")
            st.text(step['content'])
        if i < len(parsed_thoughts) - 1:
            st.markdown("--- ")

# --- Funções de Validação e Obtenção de Modelos ---
def validate_gemini_api_key(api_key):
    try:
        genai.configure(api_key=api_key)
        genai.list_models()
        return True
    except exceptions.PermissionDenied:
        st.error("Chave de API do Gemini inválida ou sem permissão.")
        return False
    except Exception as e:
        st.error(f"Ocorreu um erro ao validar a chave de API: {e}")
        return False

def get_gemini_models():
    try:
        return [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    except Exception as e:
        st.warning(f"Não foi possível buscar modelos Gemini. Verifique a API Key. Erro: {e}")
        return []