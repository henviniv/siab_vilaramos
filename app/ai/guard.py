import re

PALAVRAS_PROIBIDAS = {
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "CREATE",
    "TRUNCATE",
    "EXEC",
    "EXECUTE",
    "GRANT",
    "REVOKE",
    "COPY",
    "VACUUM",
    "ANALYZE",
    "DO",
    "CALL",
    "BEGIN",
    "COMMIT",
    "ROLLBACK",
    "SET",
    "SHOW",
}


def validar_sql(sql: str) -> bool:
    """
    Valida se o SQL gerado pela IA é seguro.

    Levanta ValueError caso encontre qualquer operação proibida.
    """

    if not sql:
        raise ValueError("SQL vazio.")

    sql = sql.strip()

    # Resposta especial da IA
    if sql == "NAO_PERMITIDO":
        raise ValueError("Pergunta não permitida.")

    # Apenas SELECT, aceitando CTEs iniciadas por WITH que terminem em SELECT.
    if not re.match(r"^\s*(SELECT|WITH)\b", sql, re.IGNORECASE):
        raise ValueError("Somente consultas SELECT são permitidas.")

    # Apenas um comando SQL
    if ";" in sql.rstrip(";"):
        raise ValueError("Múltiplos comandos SQL não são permitidos.")

    # Comentários SQL
    if "--" in sql:
        raise ValueError("Comentários SQL não são permitidos.")

    if "/*" in sql or "*/" in sql:
        raise ValueError("Comentários SQL não são permitidos.")

    # Palavras proibidas
    for palavra in PALAVRAS_PROIBIDAS:
        if re.search(rf"\b{palavra}\b", sql, re.IGNORECASE):
            raise ValueError(f"Comando proibido encontrado: {palavra}")

    return True