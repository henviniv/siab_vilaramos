from app.supabase_db import supabase


def buscar_papanicolau(micro=None):

    consulta = (
        supabase
        .table("vw_papanicolau")
        .select("*")
        .order("nome")
    )

    if micro:
        consulta = consulta.eq("micro", micro)

    resposta = consulta.execute()

    return resposta.data or []