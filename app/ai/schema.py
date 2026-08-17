DATABASE_SCHEMA = """
PostgreSQL SIAB. Gere apenas SQL SELECT para a tabela pessoas.

Tabela pessoas: id bigint, equipe text, micro text, cor_etnia text, nome text,
sus text, familia text, data_nascimento text (DD/MM/YYYY), idade integer,
genero text, gestante text, dia text, has text, hiperdia text, insulino text,
sm text, cpf text, tb text, han text, obesa text, tabagista text,
uso_de_drogas text, uso_de_alcool text, acamado text, restrito text,
asmatico_dpoc text, bolsa_familia text, ampi text, fralda text, sifilis text,
endereco text, created_at timestamp, updated_at timestamp, google_row integer.
Nunca invente tabelas, colunas ou valores.

Valores fixos:
- micro: 'MICRO 01' até 'MICRO 30' (sempre texto; ex.: micro = 'MICRO 22').
- equipe: 'EQUIPE 1' até 'EQUIPE 5' (sempre texto).
- genero: 'FEMININO' ou 'MASCULINO'. Termos mulher/menina/feminino => FEMININO;
  homem/menino/masculino => MASCULINO. Se a pergunta disser apenas pessoas,
  não filtre genero.

Famílias:
- familia identifica uma família e pode repetir em várias pessoas.
- Quantidade de famílias: COUNT(DISTINCT familia), ignorando NULL quando adequado.

Idade e datas:
- idade é integer em anos completos; use para perguntas em anos.
- Para meses, dias, bebê, recém-nascido, menor de 1 ano ou precisão inferior a anos,
  use TO_DATE(data_nascimento, 'DD/MM/YYYY') com CURRENT_DATE/INTERVAL.
- Nunca compare data_nascimento diretamente sem TO_DATE.

Campos marcados do SIAB:
- Campos de condição usam text com 'S' para sim/presente; não use TRUE/FALSE nem 'N'.
- dia = diabetes; has = hipertensão; hiperdia = hipertensão e diabetes; sm = saúde mental;
  tb = tuberculose; han = hanseníase; insulino = uso de insulina;
  asmatico_dpoc = asma/DPOC; demais condições usam o próprio nome da coluna.
- Total de diabéticos: (dia = 'S' OR hiperdia = 'S').
- Total de hipertensos: (has = 'S' OR hiperdia = 'S').
- Hiperdia especificamente: hiperdia = 'S'.

Busca textual:
- Nome e endereço devem usar ILIKE '%texto%'; não use igualdade exata para endereço.

Agregação/listagem:
- Com COUNT/SUM/AVG/MIN/MAX, toda coluna normal do SELECT deve estar no GROUP BY.
- Para contagem total, selecione só COUNT(*) AS quantidade.
- Para lista de pessoas, selecione apenas colunas úteis/relevantes (ex.: nome, familia,
  endereco, data_nascimento, idade, sus e condições pedidas). Não use SELECT *.
- Não adicione LIMIT arbitrário quando o usuário pedir todos os registros.

Redistribuição de famílias entre micros:
- Se o usuário pedir para uma micro gerar/dividir/redistribuir uma lista de famílias ou
  pessoas para outras micros responsáveis, use uma CTE com famílias distintas da micro de
  origem e NTILE pela quantidade de micros destino.
- Preserve famílias juntas: calcule micro_responsavel por familia e depois JOIN em pessoas.
- A micro de origem deve continuar no WHERE (ex.: p.micro = 'MICRO 22').
- Se a pergunta trouxer as micros destino, use exatamente elas no CASE do NTILE; se não
  trouxer, use as micros compatíveis com o contexto do usuário/pergunta.
- Exemplo de formato: WITH familias AS (SELECT familia, CASE NTILE(N) OVER (ORDER BY familia)
  WHEN 1 THEN 'MICRO XX' ... END AS micro_responsavel FROM (SELECT DISTINCT familia FROM
  pessoas WHERE micro = 'MICRO YY' AND familia IS NOT NULL) f) SELECT micro_responsavel,
  p.familia, p.nome, p.idade, p.data_nascimento, p.sus, p.endereco FROM pessoas p JOIN
  familias f ON p.familia = f.familia WHERE p.micro = 'MICRO YY' ... ORDER BY
  micro_responsavel, p.familia, p.nome.

Regras finais:
- Sempre aplique filtros de micro/equipe solicitados ou impostos pelo contexto do usuário.
- Se não for possível responder com SELECT usando a tabela/colunas disponíveis, retorne
  exatamente: NAO_PERMITIDO
"""
