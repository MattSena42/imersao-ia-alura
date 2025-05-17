import requests
import json

API_URL = "http://127.0.0.1:5000/api/buscar-vagas"

payload_vaga_simples = {
    "cargo": "Analista de Sistemas",
    "cidade_principal": "São Paulo",
    "buscar_proximas": False 
}

payload_vaga_completa = {
    "cargo": "Engenheiro de Software Pleno",
    "cidade_principal": "Curitiba",
    "buscar_proximas": True
}

payload_para_testar = payload_vaga_completa


print(f"Enviando requisição para: {API_URL}")
print(f"Com payload: {json.dumps(payload_para_testar, indent=2)}")

try:
    response = requests.post(API_URL, json=payload_para_testar, timeout=240)

    if response.ok:
        print("\nRequisição bem-sucedida!")
        data_resposta = response.json()
        
        print(f"Mensagem da API: {data_resposta.get('mensagem')}")
        
        vagas_recebidas = data_resposta.get('vagas', [])
        if vagas_recebidas:
            print(f"\n--- {len(vagas_recebidas)} Vagas Recebidas (mostrando as 3 primeiras) ---")
            for i, vaga in enumerate(vagas_recebidas[:3]):
                print(f"\n--- Vaga {i+1} (da API) ---")
                print(f"  Título: {vaga.get('titulo')}")
                print(f"  Empresa: {vaga.get('empresa')}")
                print(f"  Localização: {vaga.get('localizacao')}")
                print(f"  Data Original: {vaga.get('data_postagem_original')}")
            if len(vagas_recebidas) > 3:
                print("\n... e mais vagas.")
        else:
            print("Nenhuma vaga retornada na resposta da API.")

    else:
        print(f"\nErro na requisição: Código {response.status_code}")
        try:
            erro_data = response.json()
            print(f"Detalhes do erro (JSON): {json.dumps(erro_data, indent=2, ensure_ascii=False)}")
        except json.JSONDecodeError:
            print(f"Resposta de erro não era JSON: {response.text}")

except requests.exceptions.Timeout:
    print("\nErro: A requisição demorou demais (timeout).")
except requests.exceptions.RequestException as e:
    print(f"\nErro na requisição: {e}")