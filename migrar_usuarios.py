from werkzeug.security import generate_password_hash
from app.supabase_db import supabase
from app.auth import USERS

total = 0
ignorados = 0
erros = 0

for username, dados in USERS.items():
    try:
        # Verifica se já existe
        existente = (
            supabase
            .table("usuarios")
            .select("username")
            .eq("username", username)
            .execute()
        )

        if existente.data:
            print(f"⚠ {username} já existe.")
            ignorados += 1
            continue

        supabase.table("usuarios").insert({
            "username": username,
            "password_hash": generate_password_hash(dados["password"]),
            "role": dados["role"],
            "micro": dados.get("micro"),
            "equipe": dados.get("equipe"),
        }).execute()

        print(f"✔ {username} migrado.")
        total += 1

    except Exception as e:
        print(f"❌ Erro ao migrar {username}: {e}")
        erros += 1

print("\n========== RESUMO ==========")
print(f"Migrados : {total}")
print(f"Ignorados: {ignorados}")
print(f"Erros    : {erros}")