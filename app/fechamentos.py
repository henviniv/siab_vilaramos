from app.supabase_db import supabase


def buscar_pessoas(equipe, micro):
    resultado = (
        supabase
        .table("pessoas")
        .select("*")
        .eq("equipe", equipe)
        .eq("micro", micro)
        .execute()
    )

    return resultado.data or []


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


def gerar_fechamento_micro(equipe, micro):

    pessoas = buscar_pessoas(equipe, micro)

    tabela = []


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

        linha.append(sum(linha[1:]))

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


    for descricao, minimo, maximo in [
        ("0 a 14 anos", 0, 14),
        ("15 anos e mais", 15, None)
    ]:

        linha = [descricao]
        total = 0

        for campo in condicoes:

            valor = contar_condicao(
                pessoas,
                campo,
                minimo,
                maximo
            )

            linha.append(valor)
            total += valor

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


    return tabela