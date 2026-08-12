DATABASE_SCHEMA = """
Banco de dados PostgreSQL do sistema SIAB.

Cada registro representa uma pessoa cadastrada.

Tabela: pessoas

Colunas:

- id (bigint)
- equipe (text)
- micro (text)
- cor_etnia (text)
- nome (text)
- sus (text)
- familia (text)
- data_nascimento (text)
- idade (integer)
- genero (text)
- gestante (text)
- dia (text)
- has (text)
- hiperdia (text)
- insulino (text)
- sm (text)
- cpf (text)
- tb (text)
- han (text)
- obesa (text)
- tabagista (text)
- uso_de_drogas (text)
- uso_de_alcool (text)
- acamado (text)
- restrito (text)
- asmatico_dpoc (text)
- bolsa_familia (text)
- ampi (text)
- fralda (text)
- sifilis (text)
- endereco (text)
- created_at (timestamp)
- updated_at (timestamp)
- google_row (integer)

Nunca invente nomes de colunas.
Nunca invente tabelas.
Sempre utilize exatamente os nomes das colunas acima.

============================================================
MICRO
============================================================

A coluna "micro" é TEXT.

Os valores armazenados são exatamente:

'MICRO 01'
'MICRO 02'
'MICRO 03'
...
'MICRO 30'

Sempre compare como texto.

Exemplo correto:

WHERE micro = 'MICRO 22'

Nunca faça:

WHERE micro = 22

============================================================
EQUIPE
============================================================

A coluna "equipe" é TEXT.

Os valores armazenados são:

'EQUIPE 1'
'EQUIPE 2'
'EQUIPE 3'
'EQUIPE 4'
'EQUIPE 5'

Sempre compare como texto.

Exemplo correto:

WHERE equipe = 'EQUIPE 4'

============================================================
FAMÍLIA
============================================================

A coluna "familia" identifica uma família.

Uma família pode possuir várias pessoas.

Quando a pergunta solicitar quantidade de famílias,
utilize:

COUNT(DISTINCT familia)

Ignore famílias NULL.

Exemplo:

SELECT COUNT(DISTINCT familia)
FROM pessoas
WHERE micro = 'MICRO 22'
AND familia IS NOT NULL

============================================================
IDADE EM ANOS
============================================================

A coluna "idade" é INTEGER.

Ela representa a idade da pessoa em ANOS COMPLETOS.

Quando a pergunta informar idade em ANOS,
utilize a coluna "idade".

Exemplo:

Pessoas menores de 18 anos:

WHERE idade < 18

Pessoas maiores de 18 anos:

WHERE idade > 18

Pessoas com 18 anos ou mais:

WHERE idade >= 18

Pessoas entre 18 e 59 anos, inclusive:

WHERE idade BETWEEN 18 AND 59

IMPORTANTE:

Interprete cuidadosamente os operadores utilizados
na pergunta.

"menor que 18" significa:

idade < 18

"menor ou igual a 18" significa:

idade <= 18

"maior que 18" significa:

idade > 18

"maior ou igual a 18" significa:

idade >= 18

============================================================
FAIXAS DE IDADE EM ANOS
============================================================

Quando o usuário informar uma faixa de idade,
respeite exatamente os limites informados.

Exemplo:

"crianças de 2 até 10 anos"

significa:

idade >= 2 AND idade <= 10

Exemplo:

"maiores de 2 anos e menores de 10 anos"

significa:

idade > 2 AND idade < 10

Exemplo:

"maiores ou iguais a 2 e menores que 10"

significa:

idade >= 2 AND idade < 10

Exemplo:

"de 2 a menos de 10 anos"

significa:

idade >= 2 AND idade < 10

Exemplo:

"entre 2 e 10 anos, inclusive"

significa:

idade >= 2 AND idade <= 10

NÃO confunda:

"até 10 anos"

com:

"menores de 10 anos"

"até 10 anos" normalmente significa:

idade <= 10

"menores de 10 anos" significa:

idade < 10

============================================================
IDADE EM MESES OU DIAS
============================================================

NUNCA utilize a coluna "idade" para calcular meses ou dias
de vida.

A coluna "idade" representa somente ANOS COMPLETOS.

A coluna "data_nascimento" é TEXT no formato:

DD/MM/YYYY

Quando a pergunta mencionar:

- meses
- dias de vida
- bebê
- recém-nascido
- menor de 1 ano
- menores de X meses
- crianças de X meses
- idade em meses

SEMPRE utilize "data_nascimento".

Converta a data utilizando:

TO_DATE(data_nascimento, 'DD/MM/YYYY')

Exemplo:

Crianças com até 6 meses:

WHERE TO_DATE(data_nascimento, 'DD/MM/YYYY')
      >= CURRENT_DATE - INTERVAL '6 months'

Crianças menores de 1 ano:

WHERE TO_DATE(data_nascimento, 'DD/MM/YYYY')
      >= CURRENT_DATE - INTERVAL '1 year'

IMPORTANTE:

Não utilize:

idade <= 6

para responder:

"crianças até 6 meses".

Isso estaria errado porque "idade" representa ANOS.

============================================================
FAIXAS DE IDADE EM MESES
============================================================

Quando o usuário informar limites em meses,
utilize sempre data_nascimento.

Exemplo:

"crianças de 0 até 6 meses":

WHERE TO_DATE(data_nascimento, 'DD/MM/YYYY')
      >= CURRENT_DATE - INTERVAL '6 months'

Exemplo:

"crianças menores de 6 meses":

WHERE TO_DATE(data_nascimento, 'DD/MM/YYYY')
      > CURRENT_DATE - INTERVAL '6 months'

Exemplo:

"crianças entre 6 e 12 meses":

WHERE TO_DATE(data_nascimento, 'DD/MM/YYYY')
      >= CURRENT_DATE - INTERVAL '12 months'
AND TO_DATE(data_nascimento, 'DD/MM/YYYY')
      < CURRENT_DATE - INTERVAL '6 months'

Sempre interprete os limites de acordo com a pergunta.

# ============================================================
# GÊNERO / SEXO
# ============================================================

A coluna "genero" identifica o gênero da pessoa.

Os valores armazenados no banco são exatamente:

'FEMININO'
'MASCULINO'

NUNCA invente outros valores para a coluna genero.

Sempre utilize esses valores exatamente como estão
armazenados no banco.

---

INTERPRETAÇÃO DE TERMOS RELACIONADOS A GÊNERO:

Quando o usuário utilizar qualquer um dos termos abaixo,
interprete como gênero FEMININO:

- mulher
- mulheres
- menina
- meninas
- garota
- garotas
- feminina
- femininas
- FEMININO
- FEMININAS
- ela
- elas
- dela
- delas

Utilize:

genero = 'FEMININO'

Exemplo:

Pergunta:
"Quantas mulheres existem na Micro 23?"

SQL correto:

SELECT COUNT(*)
FROM pessoas
WHERE micro = 'MICRO 23'
AND genero = 'FEMININO'

---

Quando o usuário utilizar qualquer um dos termos abaixo,
interprete como gênero MASCULINO:

- homem
- homens
- menino
- meninos
- garoto
- garotos
- masculino
- masculinos
- MASCULINO
- MASCULINOS
- ele
- eles
- dele
- deles

Utilize:

genero = 'MASCULINO'

Exemplo:

Pergunta:
"Quantos homens existem na Micro 23?"

SQL correto:

SELECT COUNT(*)
FROM pessoas
WHERE micro = 'MICRO 23'
AND genero = 'MASCULINO'

---

IMPORTANTE:

Quando a pergunta mencionar gênero, SEMPRE aplique
o filtro correspondente na coluna "genero".

Não ignore a informação de gênero.

Exemplo:

"Quantas mulheres de 25 a 64 anos existem na Micro 23?"

Deve utilizar obrigatoriamente:

WHERE micro = 'MICRO 23'
AND genero = 'FEMININO'
AND idade >= 25
AND idade <= 64

Exemplo:

"Quantos homens de 18 a 59 anos existem na Equipe 4?"

Deve utilizar obrigatoriamente:

WHERE equipe = 'EQUIPE 4'
AND genero = 'MASCULINO'
AND idade >= 18
AND idade <= 59

---

Quando a pergunta utilizar "pessoas" sem especificar
homens, mulheres, masculino ou feminino, NÃO aplique
nenhum filtro de gênero.

Exemplo:

"Quantas pessoas de 25 a 64 anos existem na Micro 23?"

Utilize:

WHERE micro = 'MICRO 23'
AND idade >= 25
AND idade <= 64

NÃO adicione:

AND genero = 'FEMININO'

nem:

AND genero = 'MASCULINO'

---

Quando a pergunta combinar gênero com outras condições,
TODAS as condições devem ser aplicadas simultaneamente.

Exemplo:

"Quantas mulheres menores de 18 anos têm diabetes?"

Utilize:

WHERE genero = 'FEMININO'
AND idade < 18
AND (
    dia = 'S'
    OR hiperdia = 'S'
)

Exemplo:

"Quantos homens hipertensos existem na Equipe 4?"

Utilize:

WHERE equipe = 'EQUIPE 4'
AND genero = 'MASCULINO'
AND (
    has = 'S'
    OR hiperdia = 'S'
)

Nunca ignore o gênero informado na pergunta.

Nunca substitua "mulheres" por "pessoas".

Nunca substitua "homens" por "pessoas".


============================================================
SIGNIFICADO DAS SIGLAS DO SIAB
============================================================

As colunas possuem nomes abreviados.

NUNCA confunda o significado delas.

- dia = DIABETES
- has = HIPERTENSÃO ARTERIAL SISTÊMICA
- hiperdia = HIPERTENSÃO E DIABETES
- sm = SAÚDE MENTAL
- tb = TUBERCULOSE
- han = HANSENÍASE
- insulino = USO DE INSULINA
- asmatico_dpoc = ASMA OU DPOC

============================================================
DIABETES
============================================================

A coluna "dia" significa DIABETES.

"S" significa que existe registro de diabetes.

Exemplo:

WHERE dia = 'S'

IMPORTANTE:

Quando a pergunta solicitar:

- quantos diabéticos existem;
- quantas pessoas têm diabetes;
- total de diabéticos;
- pessoas diabéticas;

DEVEM SER CONSIDERADAS:

1. pessoas com dia = 'S'
2. pessoas com hiperdia = 'S'

Portanto, utilize:

WHERE dia = 'S'
   OR hiperdia = 'S'

Exemplo:

SELECT COUNT(*)
FROM pessoas
WHERE dia = 'S'
   OR hiperdia = 'S'

Se houver filtro de equipe:

SELECT COUNT(*)
FROM pessoas
WHERE equipe = 'EQUIPE 4'
AND (
    dia = 'S'
    OR hiperdia = 'S'
)

Se houver filtro de micro:

SELECT COUNT(*)
FROM pessoas
WHERE micro = 'MICRO 22'
AND (
    dia = 'S'
    OR hiperdia = 'S'
)

NÃO conte a mesma pessoa duas vezes caso ela possua
dia = 'S' E hiperdia = 'S'.

NÃO utilize a coluna "sm" para diabetes.

============================================================
HIPERTENSÃO
============================================================

A coluna "has" significa:

HIPERTENSÃO ARTERIAL SISTÊMICA.

"S" significa que existe registro de hipertensão.

Exemplo:

WHERE has = 'S'

IMPORTANTE:

Quando a pergunta solicitar:

- quantos hipertensos existem;
- quantas pessoas têm hipertensão;
- total de hipertensos;
- pessoas com pressão alta;

DEVEM SER CONSIDERADAS:

1. pessoas com has = 'S'
2. pessoas com hiperdia = 'S'

Portanto:

WHERE has = 'S'
   OR hiperdia = 'S'

Exemplo:

SELECT COUNT(*)
FROM pessoas
WHERE has = 'S'
   OR hiperdia = 'S'

Com equipe:

SELECT COUNT(*)
FROM pessoas
WHERE equipe = 'EQUIPE 4'
AND (
    has = 'S'
    OR hiperdia = 'S'
)

NÃO conte a mesma pessoa duas vezes caso ela possua
has = 'S' E hiperdia = 'S'.

============================================================
HIPERDIA
============================================================

A coluna "hiperdia" representa acompanhamento relacionado
à HIPERTENSÃO E DIABETES.

"S" significa que a pessoa possui registro no Hiperdia.

Quando a pergunta for especificamente sobre:

- pessoas no Hiperdia;
- pacientes do Hiperdia;
- acompanhamento Hiperdia;

utilize somente:

WHERE hiperdia = 'S'

Exemplo:

SELECT COUNT(*)
FROM pessoas
WHERE hiperdia = 'S'

IMPORTANTE:

Para calcular o TOTAL de diabéticos:

dia = 'S' OR hiperdia = 'S'

Para calcular o TOTAL de hipertensos:

has = 'S' OR hiperdia = 'S'

Não confunda essas três perguntas.

============================================================
OUTRAS SIGLAS
============================================================

- insulino
  = uso de insulina

- sm
  = Saúde Mental

- tb
  = Tuberculose

- han
  = Hanseníase

- asmatico_dpoc
  = Asma ou DPOC

- gestante
  = gestante

- obesa
  = pessoa obesa

- tabagista
  = tabagista

- uso_de_drogas
  = uso de drogas

- uso_de_alcool
  = uso de álcool

- acamado
  = pessoa acamada

- restrito
  = pessoa restrita

- bolsa_familia
  = recebe Bolsa Família

- ampi
  = acompanhamento AMPI

- fralda
  = utiliza fralda

- sifilis
  = registro de sífilis

============================================================
VALORES DOS CAMPOS DE CONDIÇÃO
============================================================

Os campos de condição são TEXT.

Quando uma condição está marcada:

'S' = SIM / condição presente

Não existem valores 'N'.

Quando não está marcada,
o campo pode estar vazio ou NULL.

Sempre utilize:

campo = 'S'

Nunca utilize TRUE ou FALSE.

Exemplo correto:

WHERE gestante = 'S'

Exemplos incorretos:

WHERE gestante = true

WHERE gestante = 'true'

WHERE gestante = 'N'

============================================================
ENDEREÇOS
============================================================

A coluna "endereco" contém o endereço completo.

Nunca utilize igualdade exata (=) para pesquisar endereços.

Sempre utilize ILIKE com curingas.

Exemplo correto:

WHERE endereco ILIKE '%Reverendo Erodice Pontes de Queiroz%'

Exemplo incorreto:

WHERE endereco = 'Rua Reverendo Erodice Pontes de Queiroz'

As pesquisas de endereço devem ignorar diferenças entre
letras maiúsculas e minúsculas.

============================================================
PESQUISA POR NOME
============================================================

Quando o usuário pesquisar uma pessoa pelo nome,
utilize ILIKE.

Exemplo:

WHERE nome ILIKE '%Maria%'

Não exija que o nome seja exatamente igual ao texto
informado pelo usuário.

============================================================
REGRAS IMPORTANTES DE INTERPRETAÇÃO
============================================================

1. "diabético" significa:

dia = 'S' OR hiperdia = 'S'

2. "hipertenso" significa:

has = 'S' OR hiperdia = 'S'

3. "Hiperdia" significa:

hiperdia = 'S'

4. "saúde mental" significa:

sm = 'S'

5. "tuberculose" significa:

tb = 'S'

6. "hanseníase" significa:

han = 'S'

7. Perguntas em MESES utilizam:

data_nascimento

8. Perguntas em ANOS utilizam:

idade

9. Endereço utiliza:

ILIKE '%texto%'

10. Nome utiliza:

ILIKE '%texto%'

11. Nunca invente colunas.

12. Nunca invente tabelas.

13. Nunca utilize TRUE ou FALSE nos campos de condição.

14. Nunca confunda "sm" com diabetes.

15. Nunca use "idade" para calcular idade em meses.

16. Ao contar pessoas com diabetes ou hipertensão,
não conte a mesma pessoa duas vezes.

17. Sempre aplique os filtros de micro ou equipe
solicitados pelo usuário.

"""