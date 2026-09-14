"""
Cliente da Groq.

Responsabilidades:
- Enviar perguntas para o modelo.
- Gerar SQL a partir da pergunta do usuário.
- Transformar resultados SQL em respostas em linguagem natural.
"""

import os
import re

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

    # Caso comum de COUNT(*). O prompt de SQL pede o alias ``quantidade``,
    # mas alguns drivers retornam ``count`` quando a consulta não tem alias.
    if (
        len(dados) == 1
        and isinstance(dados[0], dict)
        and len(dados[0]) == 1
        and ("quantidade" in dados[0] or "count" in dados[0])
    ):
        return {
            "quantidade": dados[0].get("quantidade", dados[0].get("count")),
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


def resposta_direta_para_contagem(pergunta: str, dados_resumidos) -> str | None:
    """Retorna uma frase natural para a faixa etária mais comum no SIAB.

    Evita uma segunda chamada à Groq para perguntas de contagem de crianças
    por idade, sem tentar adivinhar respostas para os demais tipos de consulta.
    """

    if dados_resumidos.get("tipo") != "contagem":
        return None

    pergunta_normalizada = " ".join(pergunta.lower().split())
    correspondencia = re.search(
        r"quant[oa]s?\s+(?P<grupo>.+?)\s+de\s+(?P<min>\d+)\s*(?:anos?)?"
        r"\s+(?:at[eé]\s+)?(?:at[eé]\s+)?menor(?:es)?\s+de\s+"
        r"(?P<max>\d+)\s+anos?\s+exist",
        pergunta_normalizada,
    )

    if not correspondencia:
        return None

    grupo = correspondencia.group("grupo")
    idade_minima = correspondencia.group("min")
    idade_maxima = correspondencia.group("max")
    unidade_minima = "ano" if idade_minima == "1" else "anos"
    unidade_maxima = "ano" if idade_maxima == "1" else "anos"

    return (
        f"Existem {dados_resumidos['quantidade']} {grupo} maiores de "
        f"{idade_minima} {unidade_minima} e menores de {idade_maxima} "
        f"{unidade_maxima}."
    )


def gerar_resposta(pergunta: str, sql: str, dados) -> str:
    """
    Recebe os dados do banco e gera uma resposta amigável.

    Os dados enviados para a Groq são reduzidos quando a
    consulta retorna muitos registros, evitando problemas
    de limite de contexto.

    Os dados originais continuam disponíveis para exportação.
    """

    dados_resumidos = preparar_dados_para_resposta(dados)
    resposta_direta = resposta_direta_para_contagem(pergunta, dados_resumidos)

    if resposta_direta:
        return resposta_direta

    prompt = f"""
Responda à pergunta em português do Brasil, com uma frase curta e natural
para pessoas leigas. Use somente o resultado; não mencione SQL, registros,
campos ou detalhes técnicos.

Pergunta: {pergunta}
Resultado: {dados_resumidos}
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
