from app.fechamentos import gerar_fechamento_micro
from dotenv import load_dotenv
load_dotenv()

dados = gerar_fechamento_micro(
    "EQUIPE 4",
    "MICRO 23"
)


for linha in dados:
    print(linha)