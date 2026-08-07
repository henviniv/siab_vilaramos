"""
Executa consultas SQL no banco de dados.

Este módulo recebe apenas SQL já validado pelo guard.py.
"""

from app.supabase_db import supabase


def executar_sql(sql: str):
    """
    Executa uma consulta SQL já validada e retorna o resultado.

    Args:
        sql (str): Consulta SQL validada.

    Returns:
        list: Lista de registros retornados pela consulta.
    """

    # Remove espaços e ponto e vírgula final
    # Necessário porque a RPC executa a consulta dentro de um SELECT externo
    sql = sql.strip().rstrip(";")

    resposta = supabase.rpc(
        "executar_sql",
        {"consulta": sql}
    ).execute()

    return resposta.data