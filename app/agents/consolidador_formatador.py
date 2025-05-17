import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from google.adk.agents import Agent
from app.core.config import DEFAULT_MODEL_ID, GOOGLE_API_KEY
from app.agents.utils import call_agent
from datetime import datetime, timedelta
import json
import re
import time 

AGENT_NAME = "consolidador_formatador_vagas"
VAGAS_POR_PAGINA = 3
LIMITE_ANTIGUIDADE_VAGA_DIAS = 90 
DELIMITADOR_FIM_VAGA = "---FIM_DA_VAGA---"

def criar_agente_consolidador() -> Agent:
    consolidador = Agent(
        name=AGENT_NAME,
        model=DEFAULT_MODEL_ID,
        instruction="""
        Você é um especialista em processamento de dados de vagas de emprego.
        Sua tarefa é analisar uma descrição textual de UMA VAGA DE EMPREGO e extrair as seguintes informações em formato JSON:
        - "titulo" (string, obrigatório, seja o mais específico possível com o título da vaga)
        - "empresa" (string, se disponível, senão "Não informado")
        - "localizacao" (string, cidade e estado se possível, obrigatório)
        - "data_postagem_original" (string, a data como encontrada no texto, se disponível, ex: "há 2 dias", "25/03/2024", "Publicada hoje")
        - "descricao_resumida" (string, um breve resumo da vaga ou principais requisitos, máximo 150 caracteres, foque nos aspectos chave)
        - "link" (string, se disponível)
        - "salario" (string, se disponível)

        Se uma informação não estiver claramente presente, use "Não informado" ou omita o campo (exceto título e localização).
        Se o texto de entrada não parecer ser uma descrição de vaga de emprego válida e completa, ou for apenas um fragmento sem informações chave como título ou localização, retorne um JSON com "vaga_valida": false.
        Caso contrário, retorne o JSON com "vaga_valida": true e os campos extraídos.
        """,
        description="Agente que parseia, consolida, remove duplicatas e formata vagas de emprego."
    )
    return consolidador

def parsear_vaga_individual(texto_vaga: str, agente_parser: Agent) -> dict | None:
    if not texto_vaga or not texto_vaga.strip() or len(texto_vaga.strip()) < 20:
        return None
    
    resposta_parser_str = call_agent(agent=agente_parser, message_text=texto_vaga, app_name=f"{AGENT_NAME}_parser_individual")
    
    if not resposta_parser_str or not resposta_parser_str.strip():
        time.sleep(0.2) 
        return None

    try:
        json_str_to_parse = resposta_parser_str
        if "```json" in resposta_parser_str:
            json_str_to_parse = resposta_parser_str.split("```json")[1].split("```")[0].strip()
        elif "```" in resposta_parser_str:
             json_str_to_parse = resposta_parser_str.split("```")[1].strip()

        dados_vaga = json.loads(json_str_to_parse)
        
        if not dados_vaga.get("vaga_valida", True): 
            time.sleep(0.2)
            return None
        if not dados_vaga.get("titulo") or dados_vaga.get("titulo", "não informado").lower() == "não informado" or \
           not dados_vaga.get("localizacao") or dados_vaga.get("localizacao", "não informado").lower() == "não informado":
            time.sleep(0.2)
            return None

        time.sleep(4.1) 
        return dados_vaga
            
    except json.JSONDecodeError:
        time.sleep(0.2)
        return None
    except Exception:
        time.sleep(0.2)
        return None

def normalizar_data(data_str: str | None, data_atual_cenario: datetime) -> datetime | None:
    if not data_str or data_str.lower() in ["não informado", "n/a", ""]:
        return None

    original_data_str = data_str 
    data_str_proc = data_str.lower()
    data_str_proc = data_str_proc.replace("data de publicação:", "").replace("publicada em:", "").replace("atualizada em:", "").strip()
    data_str_proc = data_str_proc.split('(')[0].strip() 

    parsed_date = None
    meses_pt = {
        'janeiro': 'January', 'fevereiro': 'February', 'março': 'March', 'abril': 'April',
        'maio': 'May', 'junho': 'June', 'julho': 'July', 'agosto': 'August',
        'setembro': 'September', 'outubro': 'October', 'novembro': 'November', 'dezembro': 'December'
    }
    for mes_pt_key, mes_en_val in meses_pt.items():
        data_str_proc = data_str_proc.replace(mes_pt_key, mes_en_val)

    formatos_data = ["%d/%m/%Y", "%d/%m/%y", "%d de %B de %Y", "%d %B %Y"]
    for fmt in formatos_data:
        try:
            temp_date = datetime.strptime(data_str_proc, fmt)
            
            parsed_date = temp_date
            return parsed_date
        except ValueError:
            continue
    
    try:
        if "hoje" in data_str_proc:
            return data_atual_cenario.replace(hour=0, minute=0, second=0, microsecond=0)
        if "ontem" in data_str_proc:
            return (data_atual_cenario - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        
        match_dias = re.search(r"há (\d+) dia(s)?", data_str_proc)
        if match_dias:
            return (data_atual_cenario - timedelta(days=int(match_dias.group(1)))).replace(hour=0, minute=0, second=0, microsecond=0)
        
        match_semanas = re.search(r"há (\d+) semana(s)?", data_str_proc)
        if match_semanas:
            return (data_atual_cenario - timedelta(weeks=int(match_semanas.group(1)))).replace(hour=0, minute=0, second=0, microsecond=0)
        
        match_horas = re.search(r"há (\d+) hora(s)?", data_str_proc)
        if match_horas:
            return data_atual_cenario.replace(hour=0, minute=0, second=0, microsecond=0)

        match_dia_mes = re.match(r"(\d{1,2})/(\d{1,2})", data_str_proc) 
        if match_dia_mes:
            dia, mes = int(match_dia_mes.group(1)), int(match_dia_mes.group(2))
            if 1 <= dia <= 31 and 1 <= mes <= 12:
                return datetime(data_atual_cenario.year, mes, dia)
    except Exception:
        pass
    
    return None

def split_into_individual_vagas(text_block: str | None, cidade_origem_busca: str = "") -> list[str]:
    if not text_block or not text_block.strip():
        return []

    text_block_sem_obs = re.split(r'\n\s*(Observaç(ão|ões)|OBS\.:|Nota:|Recomendo verificar|Além dessas)\s*:', text_block, maxsplit=1)[0].strip()
    
    vagas_raw = []
    if DELIMITADOR_FIM_VAGA in text_block_sem_obs:
        vagas_raw = [v.strip() for v in text_block_sem_obs.split(DELIMITADOR_FIM_VAGA) if v.strip() and len(v.strip()) > 20]
    else:
        regex_delimitador = r"(?m)^\s*(?:\d+\.\s*\*?|\*\s*\*?|\-\s*\*?|\*\*.+?\*\*:\s*|T[íi]tulo:\s*|Cargo:\s*|Vaga:\s*|Empresa:\s*)"
        potential_starts_indices = [match.start() for match in re.finditer(regex_delimitador, text_block_sem_obs)]
        
        if not potential_starts_indices:
            if len(text_block_sem_obs) > 40: 
                vagas_raw.append(text_block_sem_obs)
        else:
            if potential_starts_indices[0] > 0:
                first_chunk = text_block_sem_obs[:potential_starts_indices[0]].strip()
                if len(first_chunk) > 30:
                    vagas_raw.append(first_chunk)
            
            for i in range(len(potential_starts_indices)):
                start_split = potential_starts_indices[i]
                end_split = potential_starts_indices[i+1] if i + 1 < len(potential_starts_indices) else len(text_block_sem_obs)
                vaga_candidate = text_block_sem_obs[start_split:end_split].strip()
                if vaga_candidate and len(vaga_candidate) > 30 :
                    vagas_raw.append(vaga_candidate)
    
    vagas_limpas = []
    for vaga_str in vagas_raw:
        v_strip = vaga_str.strip()
        if ("empresa" in v_strip.lower() or "local" in v_strip.lower() or \
            "requisitos" in v_strip.lower() or "salário" in v_strip.lower() or \
            "descrição" in v_strip.lower() or "atividades" in v_strip.lower() or \
            "cargo" in v_strip.lower() or "título" in v_strip.lower() or "vaga" in v_strip.lower()):
            if cidade_origem_busca:
                vagas_limpas.append(f"(Origem da busca: {cidade_origem_busca}) {v_strip}")
            else:
                vagas_limpas.append(v_strip)
            
    return vagas_limpas

def processar_e_formatar_vagas(
    resultados_agente1_bruto: str | None, 
    resultados_agente2_por_cidade: dict[str, str],
    data_atual_cenario: datetime
    ) -> list[dict]:
    
    agente_parser = criar_agente_consolidador()
    vagas_parseadas_lista = []
    textos_brutos_vagas = []

    if resultados_agente1_bruto:
        textos_brutos_vagas.extend(split_into_individual_vagas(resultados_agente1_bruto, "Busca Principal"))

    for cidade, vagas_str in resultados_agente2_por_cidade.items():
        textos_brutos_vagas.extend(split_into_individual_vagas(vagas_str, cidade))

    print(f"\nAgente {AGENT_NAME}: Total de {len(textos_brutos_vagas)} descrições de vagas brutas para parsear (após split).")
    if not textos_brutos_vagas:
        return []

    for i, texto_vaga in enumerate(textos_brutos_vagas):
        vaga_parseada = parsear_vaga_individual(texto_vaga, agente_parser)
        if vaga_parseada:
            vaga_parseada['data_normalizada'] = normalizar_data(vaga_parseada.get('data_postagem_original'), data_atual_cenario)
            
            data_norm_vaga = vaga_parseada.get('data_normalizada')
            descartar_por_antiguidade = False
            if data_norm_vaga:
                if (data_atual_cenario.date() - data_norm_vaga.date()).days > LIMITE_ANTIGUIDADE_VAGA_DIAS:
                    descartar_por_antiguidade = True
            elif vaga_parseada.get('data_postagem_original','').lower() not in ["não informado", "n/a", ""]:
                match_ano_antigo = re.search(r"(201\d|202[0-3])", vaga_parseada.get('data_postagem_original', '')) 
                if match_ano_antigo :
                    ano_vaga = int(match_ano_antigo.group(1))
                    if ano_vaga < data_atual_cenario.year : 
                        data_fim_ano_vaga = datetime(ano_vaga, 12, 31)
                        if (data_atual_cenario - data_fim_ano_vaga).days > LIMITE_ANTIGUIDADE_VAGA_DIAS:
                            descartar_por_antiguidade = True
            
            if descartar_por_antiguidade:
                continue 

            if "(Origem da busca:" in texto_vaga and vaga_parseada.get('localizacao'):
                 match_origem = re.search(r"\(Origem da busca: ([^)]+)\)", texto_vaga)
                 if match_origem:
                     cidade_origem_ctx = match_origem.group(1).strip()
                     local_parseado = vaga_parseada['localizacao'].lower()
                     if cidade_origem_ctx.lower() not in local_parseado and \
                        (len(cidade_origem_ctx.split()) == 1 or cidade_origem_ctx.lower() not in " ".join(local_parseado.split()[:2])):
                         vaga_parseada['localizacao'] = f"{vaga_parseada['localizacao']} (Contexto da busca: {cidade_origem_ctx})"
            
            vagas_parseadas_lista.append(vaga_parseada)
    
    print(f"Agente {AGENT_NAME}: Total de {len(vagas_parseadas_lista)} vagas parseadas e que passaram no filtro de antiguidade.")

    vagas_unicas_dict = {}
    for vaga in vagas_parseadas_lista:
        titulo_norm = vaga.get('titulo', 's/titulo').lower().strip()
        empresa_norm = vaga.get('empresa', 's/empresa').lower().strip()
        local_norm_base = vaga.get('localizacao', 's/local').lower().split(',')[0].split('(')[0].strip()
        
        chave_unicidade = (titulo_norm, empresa_norm, local_norm_base)
        if chave_unicidade not in vagas_unicas_dict:
            vagas_unicas_dict[chave_unicidade] = vaga
        else:
            existente = vagas_unicas_dict[chave_unicidade]
            data_existente = existente.get('data_normalizada')
            data_nova = vaga.get('data_normalizada')
            if data_nova and (not data_existente or data_nova > data_existente):
                vagas_unicas_dict[chave_unicidade] = vaga 
    
    vagas_finais = list(vagas_unicas_dict.values())
    print(f"Agente {AGENT_NAME}: Total de {len(vagas_finais)} vagas únicas.")

    def sort_key(vaga):
        data_norm = vaga.get('data_normalizada')
        if data_norm and data_norm > data_atual_cenario + timedelta(days=365) : 
             return (data_atual_cenario - timedelta(days=365*10), vaga.get('titulo','z')) 
        if data_norm:
            return (data_norm, vaga.get('titulo','')) 
        return (data_atual_cenario - timedelta(days=365*20), vaga.get('titulo','z'))

    vagas_finais.sort(key=sort_key, reverse=True)
    return vagas_finais

def formatar_vaga_para_usuario(vaga: dict, indice: int, data_base_formatacao: datetime) -> str:
    saida = f"\n--- Vaga {indice + 1} ---\n"
    saida += f"🎯 Título: {vaga.get('titulo', 'N/A')}\n"
    saida += f"🏢 Empresa: {vaga.get('empresa', 'N/A')}\n"
    saida += f"📍 Localização: {vaga.get('localizacao', 'N/A')}\n"
    if vaga.get('salario') and vaga.get('salario').lower() not in ["não informado", "n/a", ""]:
        saida += f"💰 Salário: {vaga.get('salario')}\n"
    
    data_post_original = vaga.get('data_postagem_original')
    data_norm = vaga.get('data_normalizada')
    
    if data_post_original and data_post_original.lower() not in ["não informado", "n/a", ""]:
        saida += f"🗓️ Postada em: {data_post_original}"
        if data_norm:
            delta = data_base_formatacao.date() - data_norm.date()
            if delta.days == 0: saida += " (Hoje)\n"
            elif delta.days == 1: saida += " (Ontem)\n"
            elif delta.days > 1 and delta.days <= LIMITE_ANTIGUIDADE_VAGA_DIAS: saida += f" (há {delta.days} dias)\n"
            elif delta.days < 0: 
                if data_norm <= data_base_formatacao + timedelta(days=365):
                    saida += f" (Programada para: {data_norm.strftime('%d/%m/%Y')})\n"
                else: 
                    saida += f" (Data futura: {data_norm.strftime('%d/%m/%Y')})\n"
            else: 
                saida += f" (Data: {data_norm.strftime('%d/%m/%Y')})\n"
        else:
            saida += " (Data original não pôde ser processada para cálculo relativo)\n"
            
    desc = vaga.get('descricao_resumida')
    if desc and desc.lower() not in ["não informado", "n/a", ""]:
        saida += f"📝 Descrição: {desc}\n"
    
    link = vaga.get('link')
    if link and link.lower() not in ["não informado", "n/a", ""]:
        if '.' in link and ('http' in link or '/' in link or 'www' in link):
            saida += f"🔗 Link: <a href=\"{link}\" target=\"_blank\">{link}</a>\n"
        elif len(link) < 20 : 
             saida += f"🔗 Fonte/Link: {link}\n"
        else: 
            saida += f"🔗 Link (texto): {link}\n"

    return saida

if __name__ == "__main__":
    if not GOOGLE_API_KEY:
        print("API Key não carregada para o teste do consolidador.")
    else:
        print("--- Teste do Consolidador (Foco na Normalização de Datas e Filtros) ---")
        agente_teste_parser = criar_agente_consolidador()
        data_cenario_teste = datetime(2025, 5, 17) 

        print("\n--- Teste de Normalização de Datas ---")
        datas_teste = [
            "17/05/2025", "17/05/25", "17/05/68", "17/05/69", "17/05/99",
            "01/01/70", "31/12/68", "01/01/00", "Publicada em: 17 de maio de 2025", 
            "há 1 dia", "hoje", "ontem", "Data de publicação: 10 de abril de 2025", 
            "15/03/2024", "Atualizada em: 01/12", 
            "25 de março de 2025 (Vaga expirada)", "Data não informada", "há 2 horas", 
            "15/01/2023"
        ]
        for dt_str in datas_teste:
            norm = normalizar_data(dt_str, data_cenario_teste)
            print(f"'{dt_str}' -> {norm.strftime('%d/%m/%Y') if norm else 'Falhou/None'}")

        print("\n--- Teste de Parse e Filtro de Antiguidade ---")
        vaga_recente_str = f"**Dev Python Recente**\nEmpresa: StartupX\nLocal: SP\nData: há 15 dias\n{DELIMITADOR_FIM_VAGA}"
        data_limite = (data_cenario_teste - timedelta(days=LIMITE_ANTIGUIDADE_VAGA_DIAS)).strftime("%d de %B de %Y")
        vaga_no_limite_str = f"**Analista Pleno (no limite)**\nEmpresa: ConsultoriaY\nLocal: RJ\nData: {data_limite}\n{DELIMITADOR_FIM_VAGA}"
        data_antiga = (data_cenario_teste - timedelta(days=LIMITE_ANTIGUIDADE_VAGA_DIAS + 1)).strftime("%d de %B de %Y")
        vaga_antiga_filtrar_str = f"**Engenheiro Sr (antiga)**\nEmpresa: IndustriaZ\nLocal: MG\nData: {data_antiga}\n{DELIMITADOR_FIM_VAGA}"
        vaga_muito_antiga_filtrar_str = f"**Gerente 2023**\nEmpresa: MultinacionalW\nLocal: BA\nData: 15 de dezembro de 2023\n{DELIMITADOR_FIM_VAGA}"
        vaga_sem_data_str = f"**Designer UX (sem data)**\nEmpresa: EstudioCriativo\nLocal: Remoto\n{DELIMITADOR_FIM_VAGA}"

        resultados_ag1_simulado = vaga_recente_str + vaga_no_limite_str 
        resultados_ag2_simulado = { "OutraCidade": vaga_antiga_filtrar_str + vaga_muito_antiga_filtrar_str + vaga_sem_data_str }
        
        vagas_finais_teste = processar_e_formatar_vagas(
            resultados_ag1_simulado, 
            resultados_ag2_simulado, 
            data_cenario_teste
        )
        print(f"\nTotal de vagas finais no teste (esperado 3): {len(vagas_finais_teste)}")
        
        data_base_para_formatacao_teste = data_cenario_teste 
        print(f"(Formatando datas relativas a {data_base_para_formatacao_teste.strftime('%d/%m/%Y')})")

        for idx, vaga_teste_final in enumerate(vagas_finais_teste):
            print(formatar_vaga_para_usuario(vaga_teste_final, idx, data_base_para_formatacao_teste))

        print("--- Fim do Teste do Consolidador ---")