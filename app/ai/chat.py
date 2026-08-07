"""
Orquestrador da IA do SIAB.

Fluxo:

Pergunta
    ↓
Groq (gera SQL)
    ↓
Validação de segurança
    ↓
Supabase
    ↓
Groq (gera resposta em português)
    ↓
Usuário
"""

from app.ai.client import gerar_sql, gerar_resposta
from app.ai.guard import validar_sql
from app.ai.database import executar_sql


def perguntar(pergunta: str):
    """
    Recebe uma pergunta em linguagem natural e devolve uma resposta.

    Exemplo:
        "Quantas famílias existem na Micro 22?"
    """

    # 1) IA transforma a pergunta em SQL
    sql = gerar_sql(pergunta)

    # 2) Verifica se o SQL é seguro
    validar_sql(sql)

    # 3) Executa a consulta
    dados = executar_sql(sql)

    # 4) IA transforma os dados em linguagem natural
    resposta = gerar_resposta(
        pergunta=pergunta,
        sql=sql,
        dados=dados
    )

    return resposta