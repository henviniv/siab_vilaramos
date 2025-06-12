def get_sheet(planilha="EQUIPE 4", aba="MICRO 23"):
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
    sheet = client.open(planilha).worksheet(aba)

    return sheet