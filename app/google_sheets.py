import gspread
from google.oauth2.service_account import Credentials
import json
import os

def get_sheet():
    # Definir escopo de acesso à API do Google
    scope = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]

    # Carregar credenciais do JSON armazenado na variável de ambiente
    credenciais_json = os.getenv("GOOGLE_CREDS_JSON")

    if not credenciais_json:
        raise ValueError("Erro: A variável de ambiente GOOGLE_CREDS_JSON não está definida!")

    # Converter JSON de string para dicionário
    creds_info = json.loads(credenciais_json)

    # Criar credenciais usando o JSON carregado
    creds = Credentials.from_service_account_info(creds_info, scopes=scope)

    # Autenticar com o Google Sheets
    client = gspread.authorize(creds)

    # Acessar planilha e aba específicas
    sheet = client.open("EQUIPE 4").worksheet("MICRO 23")
    
    return sheet