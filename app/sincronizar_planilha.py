
"""
Sincronização somente de leitura:
Supabase (pessoas) -> Google Planilhas (Base Geral).

Este módulo nunca escreve, altera ou exclui dados no Supabase.
"""

import logging
import os
from datetime import datetime
from zoneinfo import ZoneInfo

import gspread

from app.supabase_db import supabase
from app.google_sheets import get_client


# ==========================================================
# CONFIGURAÇÕES
# ==========================================================

SPREADSHEET_ID = "1YLsa7CEPR7kzEbDduhJc1-cgI3ldNwCE79h7vS__ixA"

# Nome da aba que receberá todos os registros.
NOME_ABA = os.getenv(
    "GOOGLE_SHEET_ABA_GERAL",
    "Página1"
)

TABELA = "pessoas"

# Quantidade de registros consultados por página no Supabase.
TAMANHO_PAGINA = 1000

# Quantidade máxima de linhas enviadas por lote ao Google.
TAMANHO_LOTE_GOOGLE = 500

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)


# ==========================================================
# BUSCAR TODOS OS REGISTROS DO SUPABASE
# ==========================================================

def buscar_todas_pessoas():
    """
    Busca todas as linhas de pessoas usando paginação.

    Não utiliza limite fixo de 1000 registros no resultado final.
    """

    pessoas = []
    inicio = 0

    while True:
        fim = inicio + TAMANHO_PAGINA - 1

        resposta = (
            supabase
            .table(TABELA)
            .select("*")
            .order("id")
            .range(inicio, fim)
            .execute()
        )

        lote = resposta.data or []

        pessoas.extend(lote)

        logger.info(
            "Registros consultados: %s",
            len(pessoas)
        )

        if len(lote) < TAMANHO_PAGINA:
            break

        inicio += TAMANHO_PAGINA

    logger.info(
        "Total de registros encontrados: %s",
        len(pessoas)
    )

    return pessoas


# ==========================================================
# CONVERTER DADOS PARA O GOOGLE PLANILHAS
# ==========================================================

def converter_valor(valor):
    """
    Converte valores do Supabase para valores aceitos
    pelo Google Planilhas.
    """

    if valor is None:
        return ""

    if isinstance(valor, (dict, list)):
        import json
        return json.dumps(
            valor,
            ensure_ascii=False
        )

    if isinstance(valor, bool):
        return "S" if valor else "N"

    return valor


def preparar_dados(pessoas):
    """
    Gera o cabeçalho e as linhas da planilha.

    As colunas são obtidas dinamicamente dos registros.
    """

    if not pessoas:
        raise ValueError(
            "A consulta não retornou registros. "
            "Sincronização cancelada para preservar a planilha."
        )

    colunas = list(pessoas[0].keys())

    dados = [colunas]

    for pessoa in pessoas:
        linha = [
            converter_valor(pessoa.get(coluna))
            for coluna in colunas
        ]

        dados.append(linha)

    return dados


# ==========================================================
# ACESSAR A PLANILHA
# ==========================================================

def obter_aba():
    """
    Abre a planilha pelo ID, sem depender do título do arquivo.
    """

    cliente = get_client()

    planilha = cliente.open_by_key(
        SPREADSHEET_ID
    )

    try:
        aba = planilha.worksheet(NOME_ABA)

    except gspread.WorksheetNotFound:
        # Só cria a aba caso ela ainda não exista.
        aba = planilha.add_worksheet(
            title=NOME_ABA,
            rows=1000,
            cols=30
        )

    return aba


# ==========================================================
# ATUALIZAR A PLANILHA
# ==========================================================

def atualizar_planilha(dados):
    """
    Substitui os dados antigos pelos dados atuais.

    Os dados são enviados como RAW para evitar que textos
    sejam interpretados como fórmulas pelo Google Sheets.
    """

    aba = obter_aba()

    total_linhas = len(dados)
    total_colunas = len(dados[0])

    # Garantir espaço suficiente para todas as linhas/colunas.
    if aba.row_count < total_linhas:
        aba.add_rows(
            total_linhas - aba.row_count
        )

    if aba.col_count < total_colunas:
        aba.add_cols(
            total_colunas - aba.col_count
        )

    # Limpa os valores antigos da aba.
    # A formatação existente é preservada.
    aba.clear()

    # Enviar os dados em lotes para evitar requisições enormes.
    for inicio in range(
        0,
        total_linhas,
        TAMANHO_LOTE_GOOGLE
    ):
        fim = min(
            inicio + TAMANHO_LOTE_GOOGLE,
            total_linhas
        )

        lote = dados[inicio:fim]

        linha_inicial = inicio + 1
        linha_final = fim

        intervalo = (
            f"A{linha_inicial}:"
            f"{gspread.utils.rowcol_to_a1(linha_final, total_colunas)}"
        )

        aba.update(
            range_name=intervalo,
            values=lote,
            value_input_option="RAW"
        )

        logger.info(
            "Planilha atualizada: linhas %s até %s",
            linha_inicial,
            linha_final
        )

    # Registrar data e hora da sincronização no log.
    horario = datetime.now(
        ZoneInfo("America/Sao_Paulo")
    ).strftime("%d/%m/%Y %H:%M:%S")

    logger.info(
        "Sincronização concluída: %s registros, %s colunas. "
        "Horário: %s",
        total_linhas - 1,
        total_colunas,
        horario
    )


# ==========================================================
# EXECUÇÃO PRINCIPAL
# ==========================================================

def sincronizar():
    logger.info(
        "Iniciando sincronização Supabase -> Google Planilhas."
    )

    pessoas = buscar_todas_pessoas()

    dados = preparar_dados(pessoas)

    atualizar_planilha(dados)

    return {
        "sucesso": True,
        "registros": len(pessoas),
        "colunas": len(dados[0])
    }


if __name__ == "__main__":
    try:
        resultado = sincronizar()

        logger.info(
            "Resultado final: %s",
            resultado
        )

    except Exception:
        logger.exception(
            "Erro durante a sincronização."
        )
        raise