from flask import Blueprint, render_template
from app.google_sheets import get_sheet

bp = Blueprint('main', __name__, template_folder='../templates')

@bp.route('/')
def index():
    try:
        sheet = get_sheet()
        dados = sheet.get_all_records()

        if not dados:  # Se a planilha estiver vazia, evitar erro
            dados = [{"Erro": "Nenhum dado encontrado na planilha"}]

        print(dados)  # Log dos dados no terminal
        return render_template('index.html', dados=dados)

    except Exception as e:
        print(f"Erro ao acessar Google Sheets: {e}")
        return render_template('index.html', dados=[{"Erro": "Falha ao carregar dados"}])