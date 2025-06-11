from flask_login import UserMixin

# Classe de usuário para o Flask-Login
class User(UserMixin):
    def __init__(self, id, username, role, aba):
        self.id = id
        self.username = username
        self.role = role      # "admin" ou "micro"
        self.aba = aba        # Nome da aba no Google Sheets (ex: "MICRO 23")

# Dicionário de usuários estático (pode ser substituído por planilha ou banco depois)
USERS = {
    "admin": {
        "password": "Hidek_22",
        "role": "admin",
        "aba": None  # admin pode escolher qualquer aba
    },
    "micro23": {
        "password": "micro123",
        "role": "micro",
        "aba": "MICRO 23"
    }
}
