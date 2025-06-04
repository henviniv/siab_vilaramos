import json
import os
from google.oauth2.service_account import Credentials
import gspread

def get_sheet():
    scope = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]

    credenciais_json = os.getenv("GOOGLE_CREDS_JSON")

    if not credenciais_json:
        raise ValueError("Erro: A variável de ambiente GOOGLE_CREDS_JSON não está definida!")

    creds_info = json.loads(credenciais_json)
    creds = Credentials.from_service_account_info(creds_info, scopes=scope)

    client = gspread.authorize(creds)
    sheet = client.open("EQUIPE 4").worksheet("MICRO 23")

    return sheet
