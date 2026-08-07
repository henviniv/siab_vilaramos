"""
Cliente da Groq.

Responsabilidades:
- Enviar perguntas para o modelo.
- Gerar SQL a partir da pergunta do usuário.
- Transformar resultados SQL em respostas em linguagem natural.
"""

import os

from groq import Groq

from app.ai.prompt import SYSTEM_PROMPT


MODEL = "llama-3.3-70b-versatile"

client = Groq(
    api_key=os.environ["GROQ_API_KEY"]
)


def gerar_sql(pergunta: str) -> str:
    """
    Recebe uma pergunta em linguagem natural e devolve
    apenas uma consulta SQL.
    """

    resposta = client.chat.completions.create(
        model=MODEL,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": pergunta,
            },
        ],
    )

    sql = resposta.choices[0].message.content.strip()

    # Remove blocos ```sql ... ```
    sql = sql.replace("```sql", "")
    sql = sql.replace("```", "")
    sql = sql.strip()

    return sql


def gerar_resposta(pergunta: str, sql: str, dados) -> str:
    """
    Recebe os dados do banco e gera uma resposta amigável.
    """

    prompt = f"""
Pergunta do usuário:
{pergunta}

SQL executado:
{sql}

Resultado:
{dados}

Explique o resultado em português do Brasil.

Não invente informações.

Caso não existam registros, informe isso claramente.
"""

    resposta = client.chat.completions.create(
        model=MODEL,
        temperature=0.2,
        messages=[
            {
                "role": "system",
                "content": "Você é um assistente do sistema SIAB.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )

    return resposta.choices[0].message.content.strip()