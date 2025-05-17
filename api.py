from flask import Flask, request, jsonify
from flask_cors import CORS 

import sys
import os
import traceback

current_script_path = os.path.dirname(os.path.abspath(__file__))
project_root_directory = current_script_path
app_module_path = os.path.join(project_root_directory, 'app')

if project_root_directory not in sys.path:
    sys.path.insert(0, project_root_directory)
if app_module_path not in sys.path:
    sys.path.insert(0, app_module_path)

from app.agents.pesquisador_principal import buscar_vagas_principais
from app.agents.pesquisador_proximidade import buscar_vagas_em_proximidades
from app.agents.consolidador_formatador import processar_e_formatar_vagas
from app.core.config import GOOGLE_API_KEY
from datetime import datetime

app = Flask(__name__)
CORS(app) 

DATA_REFERENCIA_CENARIO_GEMINI = datetime(2025, 5, 17) 

@app.route('/api/buscar-vagas', methods=['POST'])
def api_buscar_vagas():
    print("[API] Nova requisição recebida para /api/buscar-vagas")
    if not GOOGLE_API_KEY:
        print("[API] ERRO: GOOGLE_API_KEY não configurada.")
        return jsonify({"erro": "Configuração da API Key do Google ausente no servidor."}), 500

    data = request.get_json()
    if not data:
        print("[API] ERRO: Payload JSON ausente ou inválido.")
        return jsonify({"erro": "Payload da requisição ausente ou inválido."}), 400

    cargo = data.get('cargo')
    cidade_principal = data.get('cidade_principal')
    buscar_proximas = data.get('buscar_proximas', False)

    if not cargo or not cidade_principal:
        print("[API] ERRO: Campos 'cargo' ou 'cidade_principal' ausentes.")
        return jsonify({"erro": "Os campos 'cargo' e 'cidade_principal' são obrigatórios."}), 400

    print(f"[API] Buscando por Cargo: '{cargo}', Cidade: '{cidade_principal}', Próximas: {buscar_proximas}")

    resultados_ag1_bruto = None
    resultados_ag2_por_cidade = {}

    try:
        print(f"[API] Etapa 1: Chamando Agente Pesquisador Principal...")
        resultados_ag1_bruto = buscar_vagas_principais(cargo, cidade_principal)
        print(f"[API] Etapa 1: Concluída. Preview Ag1: {str(resultados_ag1_bruto)[:100] if resultados_ag1_bruto else 'Nenhum resultado'}...")
        
        if buscar_proximas:
            print(f"[API] Etapa 2: Chamando Agente Pesquisador de Proximidade...")
            resultados_ag2_por_cidade = buscar_vagas_em_proximidades(cargo, cidade_principal)
            print(f"[API] Etapa 2: Concluída. Cidades próximas processadas: {len(resultados_ag2_por_cidade)}")
        else:
            print(f"[API] Etapa 2: Pular busca por proximidade.")


        print(f"[API] Etapa 3: Processando com o Agente Consolidador...")
        vagas_processadas_lista_de_dicts = processar_e_formatar_vagas(
            resultados_ag1_bruto, 
            resultados_ag2_por_cidade,
            DATA_REFERENCIA_CENARIO_GEMINI
        )
        print(f"[API] Etapa 3: Concluída. {len(vagas_processadas_lista_de_dicts)} vagas processadas.")

        if not vagas_processadas_lista_de_dicts:
            return jsonify({"mensagem": "Nenhuma vaga relevante encontrada após processamento.", "vagas": []})
        
        return jsonify({
            "mensagem": f"{len(vagas_processadas_lista_de_dicts)} vagas encontradas e processadas.",
            "vagas": vagas_processadas_lista_de_dicts
        })

    except Exception as e:
        print("[API] !!!! ERRO INESPERADO DURANTE O PROCESSAMENTO !!!!")
        print(f"[API] Tipo de Erro: {type(e).__name__}")
        print(f"[API] Mensagem do Erro: {str(e)}")
        print("[API] --- TRACEBACK COMPLETO ABAIXO ---")
        print(traceback.format_exc()) 
        print("[API] --- FIM DO TRACEBACK ---")
        return jsonify({"erro": f"Ocorreu um erro interno no servidor ao processar sua busca. Por favor, verifique os logs do servidor."}), 500

if __name__ == '__main__':
    print("Iniciando servidor Flask para a API de Vagas Gemini...")
    app.run(debug=True, use_reloader=False, port=5000)