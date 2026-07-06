import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Carrega as variáveis do .env
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL:
    raise Exception("SUPABASE_URL não encontrada.")

if not SUPABASE_KEY:
    raise Exception("SUPABASE_KEY não encontrada.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)