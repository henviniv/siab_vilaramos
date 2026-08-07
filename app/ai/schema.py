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


=========================================
REGRAS DOS CAMPOS
=========================================


A coluna "micro" é do tipo TEXT.

Os valores armazenados são exatamente:

'MICRO 01'
'MICRO 02'
'MICRO 03'
...
'MICRO 30'

Sempre compare utilizando texto.

Exemplo:

WHERE micro = 'MICRO 22'


-----------------------------------------


A coluna "equipe" é do tipo TEXT.

Os valores armazenados são:

'EQUIPE 1'
'EQUIPE 2'
'EQUIPE 3'
'EQUIPE 4'
'EQUIPE 5'

Sempre compare utilizando texto.

Exemplo:

WHERE equipe = 'EQUIPE 3'


-----------------------------------------


A coluna "familia" identifica uma família.

Uma família pode possuir várias pessoas.

Para contar famílias utilize:

COUNT(DISTINCT familia)

Ignore famílias nulas.


-----------------------------------------


A coluna "idade" é INTEGER e representa idade em ANOS completos.

Nunca utilize a coluna idade para calcular meses de vida.

Para perguntas envolvendo:

- bebês menores de 1 ano;
- crianças até X meses;
- idade em meses;

NÃO utilize a coluna idade.

Utilize a coluna data_nascimento.

A coluna data_nascimento é TEXT no formato:

DD/MM/YYYY

Para calcular idade por meses, faça conversão:

TO_DATE(data_nascimento, 'DD/MM/YYYY')

Exemplo:

Crianças até 6 meses:

WHERE TO_DATE(data_nascimento, 'DD/MM/YYYY') >= CURRENT_DATE - INTERVAL '6 months'

Crianças até 1 ano:

WHERE TO_DATE(data_nascimento, 'DD/MM/YYYY') >= CURRENT_DATE - INTERVAL '1 year'

Quando a pergunta mencionar:

- meses
- dias
- recém-nascido
- bebê
- menor de 1 ano

sempre use data_nascimento.

Quando mencionar idade em anos, utilize idade.
=========================================
SIGNIFICADO DAS SIGLAS DO SIAB
=========================================

As colunas abaixo possuem nomes abreviados.
Sempre utilize o significado correto ao interpretar
perguntas dos usuários.

- dia
  Significa DIABETES.

  Use esta coluna para perguntas relacionadas a:
  diabetes, diabéticos, pessoas com diabetes.

  Exemplo:

  WHERE dia = 'S'


- has
  Significa Hipertensão Arterial Sistêmica.

  Use esta coluna para perguntas relacionadas a:
  hipertensão, hipertensos, pressão alta.

  Exemplo:

  WHERE has = 'S'


- hiperdia
  Significa acompanhamento de Hipertensão e Diabetes.

  Use esta coluna para perguntas relacionadas a:
  pessoas acompanhadas pelo Hiperdia,
  hipertensão e diabetes acompanhados no programa.

  Exemplo:

  WHERE hiperdia = 'S'


- insulino
  Significa uso de insulina.

  Use esta coluna para perguntas relacionadas a:
  pessoas que utilizam insulina.

  Exemplo:

  WHERE insulino = 'S'


- sm
  Significa Saúde Mental.

  NÃO significa diabetes.

  Use esta coluna para perguntas relacionadas a:
  saúde mental, acompanhamento psicológico,
  transtornos mentais.

  Exemplo:

  WHERE sm = 'S'


- tb
  Significa Tuberculose.

  Use esta coluna para perguntas relacionadas a:
  tuberculose.

  Exemplo:

  WHERE tb = 'S'


- han
  Significa Hanseníase.

  Use esta coluna para perguntas relacionadas a:
  hanseníase.

  Exemplo:

  WHERE han = 'S'


- dpoc
  A coluna asmatico_dpoc representa:
  asma e doença pulmonar obstrutiva crônica.

  Use esta coluna para perguntas relacionadas a:
  asma, DPOC, problemas respiratórios.


- ampi
  Campo específico de acompanhamento do sistema.

- fralda
  Indica utilização de fralda.

- sifilis
  Indica registro de sífilis.

=========================================
CAMPOS DE ACOMPANHAMENTO
=========================================


Os campos abaixo são do tipo TEXT.

Quando uma condição está marcada no sistema,
o valor armazenado é:

'S' = Sim / condição presente


Não existem valores 'N' nesses campos.

Quando a condição não está marcada, o campo pode
estar vazio ou NULL.


Para buscar registros com determinada condição,
sempre utilize:

WHERE campo = 'S'


Campos que utilizam 'S':

- gestante
  'S' = gestante

- dia
  'S' = possui a condição registrada

- has
  'S' = possui hipertensão arterial sistêmica

- hiperdia
  'S' = participa do acompanhamento Hiperdia

- insulino
  'S' = utiliza insulina

- sm
  'S' = possui registro

- tb
  'S' = possui tuberculose

- han
  'S' = possui hanseníase

- obesa
  'S' = pessoa obesa

- tabagista
  'S' = tabagista

- uso_de_drogas
  'S' = possui registro de uso de drogas

- uso_de_alcool
  'S' = possui registro de uso de álcool

- acamado
  'S' = acamado

- restrito
  'S' = restrito

- asmatico_dpoc
  'S' = possui asma ou DPOC

- bolsa_familia
  'S' = recebe Bolsa Família

- ampi
  'S' = possui registro

- fralda
  'S' = utiliza fralda

- sifilis
  'S' = possui registro de sífilis


Nunca utilize TRUE ou FALSE nesses campos.

Exemplo correto:

WHERE gestante = 'S'


Exemplos incorretos:

WHERE gestante = true

WHERE gestante = 'true'

WHERE gestante = 'N'


=========================================
REGRAS GERAIS
=========================================

Sempre utilize os nomes das colunas exatamente como estão acima.

Nunca invente nomes de colunas.

Nunca invente tabelas.

=========================================
PESQUISA DE ENDEREÇOS
=========================================

A coluna endereco contém o endereço completo da pessoa.

Nunca utilize igualdade exata (=) para pesquisar endereços.

Sempre utilize ILIKE com curingas.

Exemplo correto:

WHERE endereco ILIKE '%Reverendo Erodice Pontes de Queiroz%'


Exemplo incorreto:

WHERE endereco = 'Rua Reverendo Erodice Pontes de Queiroz'


As pesquisas de endereço devem ignorar diferença entre
letras maiúsculas e minúsculas.

=========================================
CAMPOS DE TEXTO
=========================================

Para pesquisas por nome ou endereço,
quando o usuário não informar o texto exatamente igual
ao banco, utilize ILIKE.

Exemplos:

Nome:

WHERE nome ILIKE '%Maria%'


Endereço:

WHERE endereco ILIKE '%Rua das Flores%'

"""
