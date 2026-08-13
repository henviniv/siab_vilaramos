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


def consultar(pergunta: str, usuario=None):
    """
    Executa uma pergunta completa e retorna todos os dados
    necessários para resposta e exportação.

    Retorna:
        {
            "pergunta": pergunta_sql,
            "sql": sql,
            "dados": dados,
            "resposta": resposta
        }
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

    return {
        "pergunta": pergunta_sql,
        "sql": sql,
        "dados": dados,
        "resposta": resposta,
    }


def perguntar(pergunta: str, usuario=None):
    """
    Recebe uma pergunta em linguagem natural
    e devolve somente a resposta em português.
    """

    resultado = consultar(pergunta, usuario)

    return resultado["resposta"]


def pediu_exportacao(pergunta: str) -> bool:
    """
    Identifica se o usuário solicitou exportação dos resultados.
    """

    pergunta = pergunta.lower()

    termos_exportacao = [
        "excel",
        "planilha",
        "arquivo",
        "download",
        "baixar",
        "exportar",
        "exporte",
        "gerar lista",
        "gere uma lista",
        "gerar uma lista",
        "me dê a lista",
        "me de a lista",
        "liste as pessoas",
        "listar as pessoas",
    ]

    return any(termo in pergunta for termo in termos_exportacao)


def aplicar_contexto_usuario(pergunta: str, usuario=None):
    """
    Inclui o escopo do usuário na pergunta enviada para geração de SQL.
    """

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
            f"WHERE micro = '{micro}' em todas as consultas, salvo se "
            "a própria pergunta já trouxer um filtro de micro mais "
            "restritivo e compatível com a micro permitida."
        )

        return f"{contexto}\n\nPergunta: {pergunta}"

    if role == "admin":
        return (
            "Usuário logado com perfil administrador. "
            "Pode consultar todas as micros, a menos que a pergunta "
            "peça uma micro específica.\n\n"
            f"Pergunta: {pergunta}"
        )

    return pergunta