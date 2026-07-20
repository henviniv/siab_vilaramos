from app.supabase_db import supabase


def buscar_pessoas(equipe=None, micro=None, tamanho_pagina=1000):
    """
    Busca pessoas no Supabase, contornando o limite de registros por página.
    Se informar equipe e/ou micro, aplica os filtros.
    """

    todos_os_dados = []
    inicio = 0

    while True:

        fim = inicio + tamanho_pagina - 1

        consulta = (
            supabase
            .table("pessoas")
            .select("*")
        )

        if equipe:
            consulta = consulta.eq("equipe", equipe)

        if micro:
            consulta = consulta.eq("micro", micro)

        resposta = (
            consulta
            .range(inicio, fim)
            .execute()
        )

        pagina = resposta.data or []

        todos_os_dados.extend(pagina)

        if len(pagina) < tamanho_pagina:
            break

        inicio += tamanho_pagina

    return todos_os_dados


def idade_valida(pessoa):
    try:
        return int(pessoa.get("idade") or 0)
    except:
        return 0


def eh_s(valor):
    return str(valor or "").strip().upper() == "S"


def contar_faixa(pessoas, genero, minimo, maximo=None):

    total = 0

    for pessoa in pessoas:

        if str(pessoa.get("genero", "")).upper() != genero:
            continue

        idade = idade_valida(pessoa)

        if idade < minimo:
            continue

        if maximo is not None and idade > maximo:
            continue

        total += 1

    return total


def contar_condicao(pessoas, campo, minimo, maximo=None):

    total = 0

    for pessoa in pessoas:

        if not eh_s(pessoa.get(campo)):
            continue

        idade = idade_valida(pessoa)

        if idade < minimo:
            continue

        if maximo is not None and idade > maximo:
            continue

        total += 1

    return total


def gerar_fechamento(equipe=None, micro=None):

    pessoas = buscar_pessoas(equipe, micro)

    tabela = []
    dashboard = {}

    # ==================================================
    # POPULAÇÃO POR SEXO E FAIXA ETÁRIA
    # ==================================================

    faixas = [
        ("<1", 0, 0),
        ("1 a 4", 1, 4),
        ("5 a 6", 5, 6),
        ("7 a 9", 7, 9),
        ("10 a 14", 10, 14),
        ("15 a 19", 15, 19),
        ("20 a 39", 20, 39),
        ("40 a 49", 40, 49),
        ("50 a 59", 50, 59),
        (">60", 60, None)
    ]

    tabela.append([
        "SEXO",
        "<1",
        "1 a 4",
        "5 a 6",
        "7 a 9",
        "10 a 14",
        "15 a 19",
        "20 a 39",
        "40 a 49",
        "50 a 59",
        ">60",
        "TOTAL"
    ])

    totais_sexo = {}

    for sexo in ["MASCULINO", "FEMININO"]:

        linha = [sexo]

        for _, minimo, maximo in faixas:
            linha.append(
                contar_faixa(
                    pessoas,
                    sexo,
                    minimo,
                    maximo
                )
            )

        total_sexo = sum(linha[1:])
        linha.append(total_sexo)

        totais_sexo[sexo] = total_sexo

        tabela.append(linha)

    linha_total = ["Nº DE PESSOAS"]

    for coluna in range(1, 11):
        linha_total.append(
            tabela[1][coluna] +
            tabela[2][coluna]
        )

    linha_total.append(sum(linha_total[1:]))

    tabela.append(linha_total)

    # ==================================================
    # COR / ETNIA
    # ==================================================

    tabela.append([])

    tabela.append([
        "COR / ETNIA",
        "TOTAL"
    ])

    cores_dashboard = {}

    for cor in [
        "BRANCA",
        "PRETA",
        "PARDA",
        "AMARELA",
        "INDIGENA"
    ]:

        total_cor = sum(
            1
            for pessoa in pessoas
            if pessoa.get("cor_etnia") == cor
        )

        cores_dashboard[cor] = total_cor

        tabela.append([
            cor,
            total_cor
        ])

    # ==================================================
    # CONDIÇÕES REFERIDAS
    # ==================================================

    tabela.append([])

    tabela.append([
        "FAIXA ETÁRIA",
        "DIA",
        "HAS",
        "INSULINO",
        "TB",
        "HAN",
        "SM",
        "HIPERDIA",
        "AC",
        "TOTAL"
    ])

    condicoes = [
        "dia",
        "has",
        "insulino",
        "tb",
        "han",
        "sm",
        "hiperdia",
        "acamado"
    ]

    condicoes_dashboard = {}

    for descricao, minimo, maximo in [
        ("0 a 14 anos", 0, 14),
        ("15 anos e mais", 15, None)
    ]:

        linha = [descricao]
        total = 0

        condicoes_dashboard[descricao] = {}

        for campo in condicoes:

            valor = contar_condicao(
                pessoas,
                campo,
                minimo,
                maximo
            )

            linha.append(valor)
            total += valor

            condicoes_dashboard[descricao][campo.upper()] = valor

        linha.append(total)

        tabela.append(linha)

    # ==================================================
    # GESTANTES
    # ==================================================

    tabela.append([])

    tabela.append([
        "FAIXA ETÁRIA",
        "GESTANTES"
    ])

    gestante_10_19 = contar_condicao(
        pessoas,
        "gestante",
        10,
        19
    )

    gestante_20 = contar_condicao(
        pessoas,
        "gestante",
        20,
        None
    )

    tabela.append([
        "10 a 19 anos",
        gestante_10_19
    ])

    tabela.append([
        "20 anos e mais",
        gestante_20
    ])

    tabela.append([
        "TOTAL",
        gestante_10_19 + gestante_20
    ])

    # ==================================================
    # TOTAIS
    # ==================================================

    familias = len(
        set(
            pessoa.get("familia")
            for pessoa in pessoas
            if pessoa.get("familia")
        )
    )

    tabela.append([])

    tabela.append([
        "NUMERO DE FAMILIAS",
        familias
    ])

    tabela.append([
        "NUMERO DE PESSOAS",
        len(pessoas)
    ])

    # ==================================================
    # DASHBOARD
    # ==================================================

    dashboard["total_pessoas"] = len(pessoas)
    dashboard["total_familias"] = familias

    dashboard["sexo"] = {
        "Masculino": totais_sexo["MASCULINO"],
        "Feminino": totais_sexo["FEMININO"]
    }

    dashboard["gestantes"] = {
        "10 a 19": gestante_10_19,
        "20+": gestante_20,
        "Total": gestante_10_19 + gestante_20
    }

    dashboard["cor_etnia"] = cores_dashboard

    dashboard["condicoes"] = condicoes_dashboard

    return {
        "tabela": tabela,
        "dashboard": dashboard
    }