import os
import json
import gspread
from google.oauth2.service_account import Credentials
from google.auth import default


def get_client():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    # 🟢 Render / Local (variável de ambiente)
    credenciais_json = os.getenv("GOOGLE_CREDS_JSON")

    if credenciais_json:
        creds_info = json.loads(credenciais_json)
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)

    # 🔵 Cloud Run (service account automática do Google)
    else:
        creds, _ = default(scopes=scope)

    return gspread.authorize(creds)


def get_sheet(planilha=None, aba=None):
    if not planilha:
        raise ValueError("Você deve fornecer o nome da planilha!")
    if not aba:
        raise ValueError("Você deve fornecer o nome da aba!")

    client = get_client()

    return client.open(planilha).worksheet(aba)