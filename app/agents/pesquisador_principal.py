import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from google.adk.agents import Agent
from google.adk.tools import google_search
from app.core.config import DEFAULT_MODEL_ID, GOOGLE_API_KEY
from app.agents.utils import call_agent

AGENT_NAME = "pesquisador_principal_vagas"

def criar_agente_pesquisador_principal() -> Agent:
    pesquisador = Agent(
        name=AGENT_NAME,
        model=DEFAULT_MODEL_ID,
        instruction="""
        Você é um assistente de busca de vagas de emprego altamente eficiente.
        Sua principal tarefa é encontrar vagas de emprego para um CARGO específico em uma CIDADE_PRINCIPAL.
        Utilize a ferramenta de busca do Google (google_search) para encontrar essas vagas.
        Retorne uma lista das vagas encontradas. Para cada vaga, tente extrair e apresentar:
        - Título da vaga
        - Nome da empresa
        - Localização (se confirmar a cidade especificada ou incluir bairros)
        - Um breve resumo ou os primeiros requisitos/detalhes da vaga
        - O link para a vaga (se disponível diretamente nos resultados da busca)
        - DATA DE POSTAGEM da vaga (Ex: "há 2 dias", "em 25/03/2024")

        Seja conciso e direto ao apresentar os resultados.
        Formate a saída de forma clara, listando cada vaga.
        Concentre-se apenas nas vagas para o CARGO e CIDADE_PRINCIPAL fornecidos.

        CRÍTICO: Ao final da descrição de CADA vaga individual que você listar, adicione a string '---FIM_DA_VAGA---' em uma nova linha. 
        Certifique-se de que esta string apareça EXATAMENTE como '---FIM_DA_VAGA---' e esteja em sua própria linha, após todos os detalhes da vaga.
        Não adicione esta string após mensagens como "Nenhuma vaga encontrada". Apenas após descrições de vagas reais.
        Exemplo de formatação para UMA vaga:
        **Título da Vaga Exemplo**
        *   Empresa: Empresa Exemplo
        *   Localização: Cidade Exemplo, UF
        *   Descrição: Breve descrição aqui...
        *   Data de Postagem: Há 1 semana
        *   Link: https://exemplo.com/vaga
        ---FIM_DA_VAGA---
        """,
        description="Agente que busca vagas de emprego em uma cidade principal usando o Google Search e usa um delimitador.",
        tools=[google_search]
    )
    return pesquisador

def buscar_vagas_principais(cargo: str, cidade: str) -> str:
    agente = criar_agente_pesquisador_principal()
    entrada_agente = f"CARGO: {cargo}\nCIDADE_PRINCIPAL: {cidade}"
    
    print(f"Agente {AGENT_NAME}: Buscando vagas para '{cargo}' em '{cidade}' (com delimitador)...")
    
    resultados_brutos = call_agent(agent=agente, message_text=entrada_agente, app_name=AGENT_NAME)
    
    print(f"Agente {AGENT_NAME}: Resposta recebida.")
    return resultados_brutos

if __name__ == "__main__":
    if not GOOGLE_API_KEY:
        print("API Key não carregada. Verifique seu .env e a configuração.")
    else:
        print(f"Teste do {AGENT_NAME} iniciado. Usando modelo: {DEFAULT_MODEL_ID}")
        cargo_teste = "Desenvolvedor Backend Java"
        cidade_teste = "Campinas"
        
        vagas_encontradas = buscar_vagas_principais(cargo_teste, cidade_teste)
        
        print("\n--- Vagas Encontradas (Saída Bruta do Agente com Delimitador) ---")
        print(vagas_encontradas)
        print("----------------------------------------------------")