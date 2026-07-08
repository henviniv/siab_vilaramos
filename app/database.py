from app.supabase_db import supabase


def buscar_micro(equipe, micro):
    resposta = (
        supabase
        .table("pessoas")
        .select("*")
        .eq("equipe", equipe)
        .eq("micro", micro)
        .order("familia")
        .execute()
    )

    return resposta.data