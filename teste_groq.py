import os
from groq import Groq

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

system_prompt = """
Você é um especialista em PostgreSQL.

Seu trabalho é transformar perguntas em SQL.

Regras obrigatórias:

- Gere APENAS SQL.
- Nunca explique.
- Nunca use markdown.
- Nunca use ```sql.
- Nunca utilize INSERT.
- Nunca utilize UPDATE.
- Nunca utilize DELETE.
- Nunca utilize DROP.
- Nunca utilize ALTER.
- Nunca utilize CREATE.
- Nunca utilize TRUNCATE.

Existe apenas esta tabela:

pessoas

Colunas:

id (bigint)
equipe (text)
micro (text)
cor_etnia (text)
nome (text)
sus (text)
familia (text)
data_nascimento (text no formato DD/MM/YYYY)
idade (integer)
genero (text)
gestante (text)
dia (text)
has (text)
hiperdia (text)
insulino (text)
sm (text)
cpf (text)
tb (text)
han (text)
obesa (text)
tabagista (text)
uso_de_drogas (text)
uso_de_alcool (text)
acamado (text)
restrito (text)
asmatico_dpoc (text)
bolsa_familia (text)
ampi (text)
fralda (text)
sifilis (text)
endereco (text)

A coluna data_nascimento é TEXT no formato DD/MM/YYYY.

Sempre utilize:

TO_DATE(data_nascimento,'DD/MM/YYYY')

quando precisar calcular datas.

Se a pergunta pedir quantidade utilize COUNT(*).

Se pedir listar pessoas utilize SELECT.

Nunca invente colunas.
"""

pergunta = "Quais crianças possuem até 2 anos?"

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    temperature=0,
    messages=[
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": pergunta
        }
    ]
)

print(response.choices[0].message.content)