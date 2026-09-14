import os


os.environ.setdefault("GROQ_API_KEY", "test-key")
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_KEY", "test-key")

from app.ai.client import preparar_dados_para_resposta, resposta_direta_para_contagem


def test_reconhece_alias_quantidade_como_contagem():
    dados = preparar_dados_para_resposta([{"quantidade": 23}])

    assert dados == {
        "quantidade": 23,
        "tipo": "contagem",
        "registros": [],
    }


def test_resposta_de_faixa_etaria_e_natural_sem_chamada_ao_modelo():
    resposta = resposta_direta_para_contagem(
        "quantas crianças de 1 ate ate menor de 2 anos existem na equipe 4",
        {"quantidade": 23, "tipo": "contagem", "registros": []},
    )

    assert resposta == "Existem 23 crianças maiores de 1 ano e menores de 2 anos."
