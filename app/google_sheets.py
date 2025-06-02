import gspread
from google.oauth2.service_account import Credentials
import os

def get_sheet():
    scope = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]

    creds = Credentials.from_service_account_file(
        os.path.join(os.path.dirname(__file__), '../siab-vila-ramos-26e8cfe5c1c8.json'),
        scopes=scope
    )

    client = gspread.authorize(creds)
    sheet = client.open("EQUIPE 4").worksheet("MICRO 23")
    return sheet
