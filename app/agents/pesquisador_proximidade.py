import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from google.adk.agents import Agent
from google.adk.tools import google_search
from app.core.config import DEFAULT_MODEL_ID, GOOGLE_API_KEY
from app.agents.utils import call_agent
import re

AGENT_NAME_IDENTIFICADOR_CIDADES = "identificador_cidades_proximas"
AGENT_NAME_BUSCADOR_PROXIMIDADE = "pesquisador_vagas_proximidade"
MAX_CIDADES_PROXIMAS_PARA_BUSCA = 3

def criar_agente_identificador_cidades() -> Agent:
    identificador = Agent(
        name=AGENT_NAME_IDENTIFICADOR_CIDADES,
        model=DEFAULT_MODEL_ID,
        instruction=f"""
        Você é um assistente de pesquisa geográfica.
        Sua tarefa é identificar cidades vizinhas relevantes para busca de emprego, dada uma CIDADE_PRINCIPAL.
        Use a ferramenta google_search para encontrar essa informação.
        IMPORTANTE: Sua resposta DEVE SER APENAS uma lista de nomes de cidades, separados por vírgula.
        NÃO inclua nenhuma outra palavra, frase introdutória, numeração ou marcadores como '*'.
        Exemplo de resposta CORRETA para CIDADE_PRINCIPAL: Pindamonhangaba
        Taubaté, Guaratinguetá, São José dos Campos, Jacareí, Caçapava

        Se não encontrar cidades próximas, responda com "Nenhuma cidade próxima encontrada".
        Liste no máximo 5 cidades.
        """,
        description="Agente que identifica cidades próximas relevantes para busca de emprego.",
        tools=[google_search]
    )
    return identificador

def criar_agente_buscador_proximidade() -> Agent:
    buscador = Agent(
        name=AGENT_NAME_BUSCADOR_PROXIMIDADE,
        model=DEFAULT_MODEL_ID,
        instruction="""
        Você é um assistente de busca de vagas de emprego.
        Sua tarefa é encontrar vagas para um CARGO específico em uma CIDADE fornecida.
        Utilize a ferramenta de busca do Google (google_search).
        Retorne uma lista das vagas encontradas. Para cada vaga, tente extrair e apresentar:
        - Título da vaga
        - Nome da empresa
        - Localização (confirmando a cidade)
        - Um breve resumo ou detalhes da vaga
        - O link para a vaga (se disponível)
        - DATA DE POSTAGEM da vaga (Ex: "há 2 dias", "em 25/03/2024")
        
        Seja conciso. Formate a saída de forma clara.
        Se não encontrar vagas, informe "Nenhuma vaga encontrada para [CARGO] em [CIDADE]".

        CRÍTICO: Ao final da descrição de CADA vaga individual que você listar, adicione a string '---FIM_DA_VAGA---' em uma nova linha. 
        Certifique-se de que esta string apareça EXATAMENTE como '---FIM_DA_VAGA---' e esteja em sua própria linha, após todos os detalhes da vaga.
        Não adicione esta string após mensagens como "Nenhuma vaga encontrada". Apenas após descrições de vagas reais.
        """,
        description="Agente que busca vagas de emprego em uma cidade específica e usa um delimitador.",
        tools=[google_search]
    )
    return buscador

def identificar_cidades_proximas(cidade_principal: str) -> list[str]:
    agente_id_cidades = criar_agente_identificador_cidades()
    entrada_agente = f"CIDADE_PRINCIPAL: {cidade_principal}"
    
    resposta_bruta = call_agent(agent=agente_id_cidades, message_text=entrada_agente, app_name=AGENT_NAME_IDENTIFICADOR_CIDADES)

    cidades_encontradas = []
    if resposta_bruta and "nenhuma cidade próxima encontrada" not in resposta_bruta.lower():
        cidades_brutas = resposta_bruta.split(',')
        for cidade_str in cidades_brutas:
            nome_cidade = cidade_str.strip()
            if nome_cidade.startswith('*'):
                nome_cidade = nome_cidade[1:].strip()
            if nome_cidade.endswith('.'):
                nome_cidade = nome_cidade[:-1].strip()
            
            if nome_cidade and len(nome_cidade) > 1:
                cidades_encontradas.append(nome_cidade)
    
    cidades_filtradas = [c for c in cidades_encontradas if c.lower() != cidade_principal.lower()]
    
    print(f"Agente {AGENT_NAME_IDENTIFICADOR_CIDADES}: Cidades próximas para busca: {cidades_filtradas[:MAX_CIDADES_PROXIMAS_PARA_BUSCA]}")
    return cidades_filtradas[:MAX_CIDADES_PROXIMAS_PARA_BUSCA]

def buscar_vagas_em_proximidades(cargo: str, cidade_principal: str) -> dict[str, str]:
    cidades_proximas_para_busca = identificar_cidades_proximas(cidade_principal)
    
    if not cidades_proximas_para_busca:
        return {}

    print(f"\nAgente {AGENT_NAME_BUSCADOR_PROXIMIDADE}: Buscando vagas para '{cargo}' em: {', '.join(cidades_proximas_para_busca)}")
    
    agente_buscador = criar_agente_buscador_proximidade()
    resultados_por_cidade = {}

    for cidade_prox in cidades_proximas_para_busca:
        print(f"--- Buscando em: {cidade_prox} (com delimitador) ---")
        entrada_agente_busca = f"CARGO: {cargo}\nCIDADE: {cidade_prox}"
        try:
            app_name_chamada = f"{AGENT_NAME_BUSCADOR_PROXIMIDADE}_{cidade_prox.replace(' ','_').replace('/','_')}"
            resultados_brutos_cidade = call_agent(
                agent=agente_buscador, 
                message_text=entrada_agente_busca, 
                app_name=app_name_chamada
            )
            resultados_por_cidade[cidade_prox] = resultados_brutos_cidade
        except Exception as e:
            print(f"Erro ao buscar vagas em {cidade_prox}: {e}")
            resultados_por_cidade[cidade_prox] = f"Erro ao buscar vagas: {e}"
        
    return resultados_por_cidade

if __name__ == "__main__":
    if not GOOGLE_API_KEY:
        print("API Key não carregada. Verifique seu .env e a configuração.")
    else:
        print(f"Teste do {AGENT_NAME_BUSCADOR_PROXIMIDADE} e {AGENT_NAME_IDENTIFICADOR_CIDADES} iniciado.")
        cargo_teste = "Engenheiro Químico"
        cidade_principal_teste = "Lorena"

        resultados_proximidades = buscar_vagas_em_proximidades(cargo_teste, cidade_principal_teste)

        print("\n--- Resultados Finais da Busca por Proximidade (com Delimitador) ---")
        if resultados_proximidades:
            for cidade, vagas in resultados_proximidades.items():
                print(f"\n--- Vagas em {cidade} ---")
                print(vagas)
        else:
            print("Nenhuma vaga encontrada nas proximidades ou nenhuma cidade próxima foi processada.")
        print("----------------------------------------------------")