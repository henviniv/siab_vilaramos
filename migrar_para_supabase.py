from app.google_sheets import get_sheet
from app.supabase_db import supabase

PLANILHAS = {
    "EQUIPE 1": [
        "MI 01",
        "MI 02",
        "MI 03",
        "MI 04",
        "MI 05",
        "MI 06"
    ],
    "EQUIPE 2": [
        "MICRO 7",
        "MICRO 8",
        "MICRO 9",
        "MICRO 10",
        "MICRO 11",
        "MICRO 12"
    ],
    "EQUIPE 3": [
        "MICRO 13",
        "MICRO 14",
        "MICRO 15",
        "MICRO 16",
        "MICRO 17",
        "MICRO 18"
    ],
    "EQUIPE 4": [
        "MICRO 19",
        "MICRO 20",
        "MICRO 21",
        "MICRO 22",
        "MICRO 23",
        "MICRO 24"
    ],
    "EQUIPE 5": [
        "MICRO 25",
        "MICRO 26",
        "MICRO 27",
        "MICRO 28",
        "MICRO 29",
        "MICRO 30"
    ]
}


def texto(valor):
    if valor is None:
        return ""
    return str(valor).strip()


total = 0

for equipe, micros in PLANILHAS.items():

    print(f"\n===== {equipe} =====")

    for micro in micros:

        print(f"Importando {micro}...")

        sheet = get_sheet(planilha=equipe, aba=micro)

        linhas = sheet.get_all_records()

        qtd = 0

        for numero_linha, linha in enumerate(linhas, start=2):

            if not texto(linha.get("NOME")):
                continue

            registro = {

                "equipe": equipe,
                "micro": micro,
                "google_row": numero_linha,

                "cor_etnia": texto(linha.get("COR/ETNIA")),
                "nome": texto(linha.get("NOME")),
                "sus": texto(linha.get("SUS")),
                "familia": texto(linha.get("FAMILIA") or linha.get("FAMÍLIA")),
                "data_nascimento": texto(linha.get("DATA DE NASCIMENTO")),
                "idade": texto(linha.get("IDADE")),
                "genero": texto(linha.get("GENERO")),
                "gestante": texto(linha.get("GESTANTE")),
                "dia": texto(linha.get("DIA")),
                "has": texto(linha.get("HAS")),
                "hiperdia": texto(linha.get("HIPERDIA")),
                "insulino": texto(linha.get("INSULINO")),
                "sm": texto(linha.get("SM")),
                "cpf": texto(linha.get("CPF")),
                "tb": texto(linha.get("TB")),
                "han": texto(linha.get("HAN")),
                "obesa": texto(linha.get("OBESA")),
                "tabagista": texto(linha.get("TABAGISTA")),
                "uso_de_drogas": texto(linha.get("USO DE DROGAS")),
                "uso_de_alcool": texto(linha.get("USO DE ALCOOL")),
                "acamado": texto(linha.get("ACAMADO")),
                "restrito": texto(linha.get("RESTRITO")),
                "asmatico_dpoc": texto(linha.get("ASMÁTICO DPOC")),
                "bolsa_familia": texto(linha.get("BOLSA FAMÍLIA")),
                "ampi": texto(linha.get("AMPI")),
                "fralda": texto(linha.get("FRALDA")),
                "sifilis": texto(linha.get("SIFILIS")),
                "endereco": texto(linha.get("ENDEREÇO"))
            }

            supabase.table("pessoas").upsert(
                registro,
                on_conflict="equipe,micro,google_row"
            ).execute()

            qtd += 1
            total += 1

        print(f"{micro}: {qtd} pessoas")

print("\n=================================")
print(f"TOTAL IMPORTADO: {total}")
print("=================================")