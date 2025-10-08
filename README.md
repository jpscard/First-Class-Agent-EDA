# ✨ First Class Agent EDA

## 🚀 Visão Geral do Projeto

Bem-vindo ao **First Class Agent EDA**! Este sistema inovador transforma a maneira como você interage com seus dados. Utilizando o poder dos Grandes Modelos de Linguagem (LLMs) do Google Gemini e agentes inteligentes, a aplicação permite que você realize Análise Exploratória de Dados (EDA) em arquivos CSV através de uma interface de chat intuitiva e interativa.

Com este agente, você pode:
*   **Conversar com seus Dados:** Faça perguntas em linguagem natural e obtenha respostas, insights e resumos.
*   **Gerar Visualizações:** Solicite a criação de múltiplos gráficos para visualizar tendências e padrões.
*   **Exportar Relatórios em PDF:** Gere um relatório completo da sua análise, incluindo um sumário executivo criado por IA.
*   **Acompanhar o Raciocínio:** Ative o "Modo Desenvolvedor" para seguir o passo a passo do agente de IA.

## 🌟 Funcionalidades Principais

*   **Autenticação Segura:** Login com validação ativa de API Key do Google Gemini.
*   **Interface Moderna:** Tela de boas-vindas com design baseado em cards e instruções claras.
*   **Upload de CSV:** Carregue facilmente seus arquivos de dados para análise.
*   **Agente de EDA Inteligente:** Um agente baseado em LangChain, com um prompt robusto que o instrui a ser proativo e seguir as melhores práticas de EDA.
*   **Geração de Múltiplos Gráficos:** Capacidade de gerar e exibir múltiplos gráficos em uma única resposta, com gestão de arquivos temporários para não poluir o projeto.
*   **Geração de Relatórios em PDF:** Exporte a sessão de análise completa, incluindo:
    *   Um **Sumário Executivo** gerado por IA com os principais insights.
    *   O histórico detalhado da conversa.
    *   Todos os gráficos gerados.
*   **Controles de Sessão:** Botões para "Reiniciar Chat" (limpando a análise atual, incluindo o arquivo) e "Logout".
*   **Modo Desenvolvedor:** Visualize o "pensamento" detalhado do agente para depuração e aprendizado.

## 📂 Estrutura do Projeto

O projeto é modularizado para facilitar a manutenção e expansão:

```
.
├── .gitignore              # Arquivos e pastas a serem ignorados pelo Git
├── .streamlit/             # Configurações do Streamlit (ex: tema)
│   └── config.toml
├── asset/                  # Ativos do projeto (ex: LOGO.png)
│   └── LOGO.png
├── views/                  # Módulos da interface (páginas)
│   ├── login.py
│   ├── main_app.py
│   └── welcome.py
├── utils.py                # Funções utilitárias (validação, PDF, etc.)
├── app.py                  # Ponto de entrada principal e roteador
├── requirements.txt        # Dependências do projeto
├── DejaVuSans.ttf          # (Opcional) Fonte para melhor qualidade do PDF
└── README.md               # Este arquivo
```

## 🛠️ Como Usar

### Pré-requisitos

*   **Python 3.9+**
*   **Google Gemini API Key:** Necessária para autenticação e para o funcionamento do agente. Obtenha a sua em [Google AI Studio](https://aistudio.google.com/app/apikey).
*   **(Opcional, mas recomendado) Fonte DejaVuSans:** Para a melhor qualidade na geração de relatórios em PDF, baixe o arquivo `DejaVuSans.ttf` e coloque-o na pasta raiz do projeto.

### Instalação

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/jpscard/First-Class-Agent-EDA.git
    cd First-Class-Agent-EDA
    ```

2.  **Crie e ative um ambiente virtual:**
    ```bash
    python -m venv .venv
    # No Windows
    .venv\Scripts\activate
    # No macOS/Linux
    source .venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

### Executando o Aplicativo

1.  **Execute o aplicativo Streamlit:**
    ```bash
    streamlit run app.py
    ```
2.  Abra o navegador na URL fornecida (geralmente `http://localhost:8501`).

### Uso Básico

1.  **Tela de Boas-Vindas:** Leia as instruções e clique em "Iniciar Análise".
2.  **Login:** Insira seu nome e sua API Key do Google Gemini.
3.  **Aplicação Principal:**
    *   Faça o upload de um arquivo CSV na barra lateral.
    *   Comece a fazer perguntas sobre seus dados na caixa de chat!
    *   Use os botões "Gerar Relatório em PDF" ou "Reiniciar Chat" conforme necessário.

## 👨‍💻 Desenvolvedor

**João Paulo Cardoso**
*   **LinkedIn:** [https://www.linkedin.com/in/joao-paulo-cardoso/](https://www.linkedin.com/in/joao-paulo-cardoso/)
*   **GitHub do Projeto:** [https://github.com/jpscard/First-Class-Agent-EDA](https://github.com/jpscard/First-Class-Agent-EDA)

---
*Este projeto foi desenvolvido com a ajuda de um assistente de IA.*