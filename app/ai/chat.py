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


def perguntar(pergunta: str, usuario=None):
    """
    Recebe uma pergunta em linguagem natural e devolve uma resposta.

    Exemplo:
        "Quantas famílias existem na Micro 22?"
    """

    pergunta_sql = aplicar_contexto_usuario(pergunta, usuario)

    # 1) IA transforma a pergunta em SQL
    sql = gerar_sql(pergunta_sql)

    # 2) Verifica se o SQL é seguro
    validar_sql(sql)

    # 3) Executa a consulta
    dados = executar_sql(sql)

    # 4) IA transforma os dados em linguagem natural
    resposta = gerar_resposta(
        pergunta=pergunta_sql,
        sql=sql,
        dados=dados
    )

    return resposta

def aplicar_contexto_usuario(pergunta: str, usuario=None) -> str:
    """Inclui o escopo do usuário na pergunta enviada para geração de SQL."""

    if not usuario or not getattr(usuario, "is_authenticated", False):
        return pergunta

    role = getattr(usuario, "role", None)
    micro = getattr(usuario, "micro", None)
    equipe = getattr(usuario, "equipe", None)

    if role == "micro" and micro:
        contexto = (
            f"Usuário logado: {usuario.username}. "
            f"Perfil: micro. Micro permitida: {micro}."
        )
        if equipe:
            contexto += f" Equipe permitida: {equipe}."
        contexto += (
            " Para esta pergunta, aplique obrigatoriamente o filtro "
            f"WHERE micro = '{micro}' em todas as consultas, salvo se a própria pergunta "
            "já trouxer um filtro de micro mais restritivo e compatível com a micro permitida."
        )
        return f"{contexto}\n\nPergunta: {pergunta}"

    if role == "admin":
        return (
            "Usuário logado com perfil administrador. "
            "Pode consultar todas as micros, a menos que a pergunta peça uma micro específica.\n\n"
            f"Pergunta: {pergunta}"
        )

    return pergunta
