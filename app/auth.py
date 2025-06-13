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
        "password": "senha23",
        "role": "micro",
        "aba": "MICRO 23"
    },
    ,
    "micro19": {
        "password": "senha19",
        "role": "micro",
        "aba": "MICRO 19"
    },
    "micro20": {
        "password": "senha20",
        "role": "micro",
        "aba": "MICRO 20"
    },
    ,
    "micro21": {
        "password": "senha21",
        "role": "micro",
        "aba": "MICRO 21"
    },
    "micro22": {
        "password": "senha22",
        "role": "micro",
        "aba": "MICRO 22"
    },
    "micro24": {
        "password": "senha24",
        "role": "micro",
        "aba": "MICRO 24"
    }
}
