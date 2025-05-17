# 📁 Buscador de Vagas Inteligente com IA Gemini

> Uma aplicação web que utiliza a Inteligência Artificial Google Gemini e uma arquitetura de múltiplos agentes para buscar, processar e apresentar vagas de emprego de forma amigável ao usuário. Este projeto foi desenvolvido como parte da **Imersão IA da Alura + Google**.

---

## 📌 Funcionalidades

-   ✅ **Busca Personalizada:** O usuário insere o cargo desejado e a cidade principal.
-   ✅ **Busca Abrangente:** Opção de expandir a busca para cidades próximas à localidade principal.
-   ✅ **Processamento Inteligente com Múltiplos Agentes:**
    -   Um agente focado em pesquisar vagas na cidade principal.
    -   Um agente para identificar cidades vizinhas e buscar oportunidades nelas.
    -   Um agente consolidador que analisa, remove duplicatas, filtra vagas muito antigas (mais de 3 meses) e formata os resultados.
-   ✅ **Resultados Claros e Organizados:** As vagas são apresentadas em uma interface web limpa, com informações chave como título, empresa, localização, data de postagem, descrição e link (quando disponível).
-   ✅ **Paginação:** Os resultados são paginados para facilitar a navegação.
-   ✅ **Interface Web Interativa:** Frontend desenvolvido com HTML, CSS e JavaScript para interação do usuário.
-   ✅ **API Backend:** Uma API Flask serve os dados processados para o frontend.

---

## ✨ Arquitetura do Sistema

O projeto utiliza uma arquitetura baseada em múltiplos agentes de IA para dividir e conquistar as tarefas de busca e processamento:

1.  **Agente Pesquisador Principal:** Recebe o cargo e a cidade principal do usuário. Utiliza a ferramenta `google_search` (via API Gemini) para encontrar vagas correspondentes.
2.  **Agente Pesquisador de Proximidade:**
    *   Identifica cidades geograficamente próximas à cidade principal informada (usando um agente LLM com `google_search`).
    *   Busca vagas para o mesmo cargo nessas cidades próximas, também com `google_search`.
    *   Este agente é acionado opcionalmente, conforme escolha do usuário.
3.  **Agente Consolidador e Formatador:**
    *   Recebe os resultados textuais brutos dos agentes pesquisadores.
    *   Utiliza um agente LLM para **parsear** cada descrição de vaga, extraindo informações estruturadas (título, empresa, localização, data, descrição, link, salário) em formato JSON.
    *   **Normaliza as datas** de postagem para um formato consistente.
    *   **Filtra vagas muito antigas** (mais de 90 dias).
    *   **Remove vagas duplicadas** com base em título, empresa e localização.
    *   **Ordena** as vagas (priorizando as mais recentes).
    *   Prepara os dados para serem enviados à interface do usuário.

A comunicação entre o frontend e o backend é feita através de uma API RESTful desenvolvida com Flask.

---

## 🚀 Tecnologias Utilizadas

-   **Backend:**
    -   Python 3.x
    -   Google Gemini API (para acesso aos modelos de IA generativa)
    -   `google-adk` (Framework de Agentes do Google para interagir com Gemini)
    -   Flask (para criação da API RESTful)
    -   Flask-CORS (para permitir requisições do frontend)
    -   `python-dotenv` (para gerenciamento de variáveis de ambiente, como a API Key)
-   **Frontend:**
    -   HTML5
    -   CSS3
    -   JavaScript (vanilla, com uso da `fetch` API)
-   **Ferramentas e Práticas:**
    -   Ambiente Virtual Python (`venv`)
    -   `pip` para gerenciamento de pacotes
    -   Git e GitHub para versionamento de código

---

## 📸 Demonstração

[![Imersão IA Alura + Google Gemini: Seu Buscador Inteligente de Vagas](https://img.youtube.com/vi/TPHZOjD-SAw/maxresdefault.jpg)](https://www.youtube.com/watch?v=TPHZOjD-SAw)

---

## 💻 Como Usar

1.  **Pré-requisitos:**
    *   Python 3.9 ou superior instalado.
    *   `pip` (gerenciador de pacotes Python) instalado.

2.  **Configuração do Projeto:**
    *   Clone o repositório:
        ```bash
        git clone https://github.com/MattSena42/imersao-ia-alura.git
        ```
    *   Navegue para a pasta do projeto:
        ```bash
        cd gemini_job_search_agent
        ```
    *   Crie e ative um ambiente virtual:
        ```bash
        python -m venv venv
        ```
        *   No Windows (cmd/powershell): `.\venv\Scripts\activate`
        *   No Linux/macOS (bash/zsh): `source venv/bin/activate`
    *   Instale as dependências:
        ```bash
        pip install -r requirements.txt
        ```
    *   Configure sua API Key do Google Gemini:
        1.  Crie um arquivo chamado `.env` na raiz do projeto.
        2.  Adicione sua chave ao arquivo, como no exemplo em `.env.example`:
            ```
            GOOGLE_API_KEY="SUA_CHAVE_API_DO_GEMINI_AQUI"
            ```

3.  **Executando a Aplicação:**
    *   **Inicie o servidor da API (Backend):**
        No seu terminal (com o ambiente virtual ativado), execute:
        ```bash
        python api.py
        ```
        O servidor Flask iniciará, geralmente em `http://127.0.0.1:5000`. Mantenha este terminal rodando.
    *   **Abra o Frontend:**
        Navegue até a pasta `frontend/` e abra o arquivo `index.html` no seu navegador web preferido.
    *   Utilize a interface para buscar as vagas!

4.  **(Opcional) Testando a API com Cliente Python:**
    *   Com o servidor `api.py` rodando, abra um *novo terminal* (com o ambiente virtual ativado) e execute:
        ```bash
        python test_api_client.py
        ```
    Isso enviará uma requisição de teste para a API e imprimirá a resposta no console.

---

## 🎯 Desafios Enfrentados e Aprendizados

*   **Gerenciamento de Limites de Taxa (Rate Limiting) da API Gemini:** A API possui limites de requisições por minuto. Para o Agente Consolidador, que faz uma chamada para parsear cada vaga, foi necessário implementar um `time.sleep()` para evitar exceder esses limites no *free tier*. Uma futura otimização seria o parse em lote.
*   **Parsing de Dados Não Estruturados:** Transformar o texto bruto das descrições de vagas (retornado pela busca do Google) em dados estruturados (JSON) exigiu um prompting cuidadoso para o agente LLM e tratamento de respostas que nem sempre seguiam o formato esperado.
*   **Normalização de Datas:** As datas de postagem das vagas vêm em diversos formatos ("há X dias", "dd/mm/yyyy", "Nome do Mês dd, yyyy"). Criar uma função para normalizá-las para objetos `datetime` foi essencial para o filtro de antiguidade e ordenação.
*   **Orquestração de Múltiplos Agentes:** Coordenar a passagem de informações entre os diferentes agentes (Pesquisadores -> Consolidador) e garantir que cada um cumprisse seu papel foi um aspecto central da arquitetura.
*   **Divisão de Vagas (Splitting):** Instruir os agentes de busca a usarem um delimitador explícito (`---FIM_DA_VAGA---`) entre as vagas foi crucial para melhorar a confiabilidade da separação das vagas antes do parse pelo Agente Consolidador.

---

## 🔄 Futuras Melhorias

-   **Otimização de Performance (Rate Limit):** Implementar "batch processing" no Agente Consolidador, onde múltiplas descrições de vagas são enviadas em uma única chamada à API Gemini para parseamento, reduzindo drasticamente o número total de requisições e eliminando a necessidade de `time.sleep()`.
-   **Interface de Usuário (UI/UX) Mais Rica:**
    *   Adicionar filtros avançados (tipo de contrato, nível da vaga, faixa salarial).
    *   Melhorar o feedback visual durante o carregamento (ex: spinner/loader animado).
    *   Opção de ordenar os resultados por diferentes critérios no frontend.
-   **Qualidade da Extração de Dados:**
    *   Refinar as instruções do agente parser para melhorar a extração de campos como "empresa" ou "salário" quando estiverem implícitos.
    *   Implementar um sub-agente para tentar encontrar a fonte original da vaga ou o nome da empresa se o link principal for de um agregador.
-   **Internacionalização:** Permitir busca de vagas em diferentes idiomas e regiões (exigiria ajustes nos prompts e possivelmente na lógica de cidades próximas).
-   **Testes Automatizados:** Adicionar testes unitários e de integração para garantir a robustez do backend e da API.
-   **Cache de Resultados:** Para buscas repetidas, implementar um sistema de cache para retornar resultados mais rapidamente e reduzir chamadas à API.

---

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE.txt` para mais detalhes.

---

## 👨‍💻 Autor

Feito por **Matheus Sena**
[🔗 GitHub](https://github.com/MattSena42) | [🔗 LinkedIn](https://www.linkedin.com/in/matheus-sena/)
