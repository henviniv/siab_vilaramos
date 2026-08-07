import re

PALAVRAS_PROIBIDAS = [
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
]


def validar_sql(sql):
    sql = sql.strip()

    if not sql.upper().startswith("SELECT"):
        raise ValueError("Somente SELECT é permitido.")

    if ";" in sql[:-1]:
        raise ValueError("Múltiplos comandos não são permitidos.")

    for palavra in PALAVRAS_PROIBIDAS:
        if re.search(rf"\b{palavra}\b", sql, re.IGNORECASE):
            raise ValueError(f"Comando proibido: {palavra}")

    return True