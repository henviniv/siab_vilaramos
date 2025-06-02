from flask import Blueprint, render_template
from app.google_sheets import get_sheet

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    sheet = get_sheet()
    dados = sheet.get_all_records()
    print(dados)  # Coloque aqui, antes do return
    return render_template('index.html', dados=dados)
