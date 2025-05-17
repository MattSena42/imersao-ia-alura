import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.agents.pesquisador_principal import buscar_vagas_principais
from app.agents.pesquisador_proximidade import buscar_vagas_em_proximidades
from app.agents.consolidador_formatador import (
    processar_e_formatar_vagas,
    formatar_vaga_para_usuario,
    VAGAS_POR_PAGINA
)
from app.core.config import GOOGLE_API_KEY
from datetime import datetime

def run_job_search_app():
    if not GOOGLE_API_KEY:
        print("ERRO: GOOGLE_API_KEY não encontrada. Verifique seu arquivo .env e app/core/config.py.")
        return

    print("🚀 Bem-vindo ao Gemini Job Search Agent! 🚀")

    cargo_desejado = input("💼 Qual cargo você está buscando? ")
    cidade_principal = input("🏙️ Em qual cidade principal? ")

    if not cargo_desejado or not cidade_principal:
        print("Cargo e cidade são obrigatórios. Encerrando.")
        return

    data_referencia_cenario_gemini = datetime(2025, 5, 17) 
    data_hoje_real = datetime.now() 
    
    print(f"(Contexto Dev: Buscas Gemini interpretadas como se 'hoje' fosse {data_referencia_cenario_gemini.strftime('%d/%m/%Y')})")
    print(f"(Contexto Usuário: Datas relativas ('há X dias') calculadas a partir de {data_hoje_real.strftime('%d/%m/%Y')})")

    print(f"\n🔎 Iniciando busca por '{cargo_desejado}' em '{cidade_principal}'...")

    resultados_agente1_bruto = buscar_vagas_principais(cargo_desejado, cidade_principal)
    
    print("\n📋 Preview Resultados Brutos da Busca na Cidade Principal (Agente 1):")
    if resultados_agente1_bruto and resultados_agente1_bruto.strip():
        print(f"{resultados_agente1_bruto[:300].strip()}", end="")
        if len(resultados_agente1_bruto) > 300: print("...")
        else: print()
    else:
        print(f"Nenhuma vaga encontrada para '{cargo_desejado}' em '{cidade_principal}' pelo agente principal.")
        resultados_agente1_bruto = None

    resultados_agente2_por_cidade = {} 
    buscar_proximidades_input = input("\n🤔 Deseja buscar vagas em cidades próximas também? (s/n): ").strip().lower()
    if buscar_proximidades_input == 's':
        print(f"\n🔎 Iniciando busca por '{cargo_desejado}' em cidades próximas a '{cidade_principal}'...")
        resultados_agente2_por_cidade = buscar_vagas_em_proximidades(cargo_desejado, cidade_principal)
        
        if resultados_agente2_por_cidade:
            print("\n📋 Preview Resultados Brutos da Busca em Cidades Próximas (Agente 2):")
            for cidade, vagas_str in resultados_agente2_por_cidade.items():
                print(f"\n--- Preview em {cidade} ---")
                if vagas_str and vagas_str.strip():
                    print(f"{vagas_str[:200].strip()}", end="")
                    if len(vagas_str) > 200: print("...")
                    else: print()
                else:
                    print(f"Nenhuma vaga encontrada para '{cargo_desejado}' em '{cidade}'.")
        else:
            print(f"Nenhuma vaga encontrada em cidades próximas ou nenhuma cidade próxima foi processada.")
    else:
        print("\nOk, não buscaremos em cidades próximas.")

    print("\n🎨 Agente Consolidador e Formatador processando os resultados...")
    vagas_processadas = processar_e_formatar_vagas(
        resultados_agente1_bruto,
        resultados_agente2_por_cidade,
        data_referencia_cenario_gemini 
    )

    if not vagas_processadas:
        print("\n😕 Nenhuma vaga relevante encontrada ou processada após consolidação e filtros.")
    else:
        print(f"\n✨ Total de {len(vagas_processadas)} vagas relevantes encontradas! ✨")
        
        indice_atual = 0
        mostrar_mais = True
        while mostrar_mais and indice_atual < len(vagas_processadas):
            print(f"\n--- Mostrando vagas {indice_atual + 1} a {min(indice_atual + VAGAS_POR_PAGINA, len(vagas_processadas))} (de {len(vagas_processadas)}) ---")
            for _ in range(VAGAS_POR_PAGINA):
                if indice_atual < len(vagas_processadas):
                    print(formatar_vaga_para_usuario(vagas_processadas[indice_atual], indice_atual, data_hoje_real))
                    indice_atual += 1
                else:
                    break 
            
            if indice_atual < len(vagas_processadas):
                ver_mais_input = input(f"Mostrar mais vagas? (total restante: {len(vagas_processadas) - indice_atual}) (s/n): ").strip().lower()
                if ver_mais_input != 's':
                    mostrar_mais = False
            else:
                print("\nFim de todas as vagas encontradas.")
                mostrar_mais = False
    
    print("\n✅ Busca e apresentação concluídas.")

if __name__ == "__main__":
    run_job_search_app()