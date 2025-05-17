import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("A variável de ambiente GOOGLE_API_KEY não foi configurada. "
                     "Por favor, crie um arquivo .env e adicione GOOGLE_API_KEY=SUA_CHAVE_AQUI")

DEFAULT_MODEL_ID = "gemini-2.0-flash"