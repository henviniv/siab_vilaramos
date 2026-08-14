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


MODEL = "openai/gpt-oss-120b"

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


def preparar_dados_para_resposta(dados, limite=20):
    """
    Prepara os dados retornados pelo banco antes de enviá-los
    para a Groq.

    Evita enviar milhares de registros para o modelo e
    ultrapassar o limite de contexto.

    A função NÃO altera os dados originais usados para
    exportação. Ela cria apenas uma versão reduzida para
    geração da resposta textual.
    """

    if not dados:
        return {
            "quantidade": 0,
            "registros": [],
        }

    # Caso comum de COUNT(*)
    if (
        len(dados) == 1
        and isinstance(dados[0], dict)
        and "count" in dados[0]
    ):
        return {
            "quantidade": dados[0]["count"],
            "tipo": "contagem",
            "registros": [],
        }

    quantidade = len(dados)

    # Consultas pequenas:
    # envia todos os registros.
    if quantidade <= limite:
        return {
            "quantidade": quantidade,
            "tipo": "registros",
            "registros": dados,
        }

    # Consultas grandes:
    # envia somente uma amostra dos registros.
    return {
        "quantidade": quantidade,
        "tipo": "registros",
        "observacao": (
            f"A consulta retornou {quantidade} registros. "
            f"Mostrando apenas os primeiros {limite} registros "
            "para análise da resposta."
        ),
        "registros": dados[:limite],
    }


def gerar_resposta(pergunta: str, sql: str, dados) -> str:
    """
    Recebe os dados do banco e gera uma resposta amigável.

    Os dados enviados para a Groq são reduzidos quando a
    consulta retorna muitos registros, evitando problemas
    de limite de contexto.

    Os dados originais continuam disponíveis para exportação.
    """

    dados_resumidos = preparar_dados_para_resposta(dados)

    prompt = f"""
Pergunta do usuário:
{pergunta}

SQL executado:
{sql}

Resultado da consulta:
{dados_resumidos}

Explique o resultado em português do Brasil.

Regras:
- Não invente informações.
- Use somente informações presentes no resultado da consulta.
- Se a consulta for uma contagem, informe claramente a quantidade encontrada.
- Se não existirem registros, informe isso claramente.
- Se o resultado tiver muitos registros e estiver mostrando apenas uma amostra,
  não diga que a amostra representa todos os registros.
- Quando houver uma quantidade total disponível, use essa quantidade.
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