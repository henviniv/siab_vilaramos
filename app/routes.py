from flask import Blueprint, render_template, request, redirect, url_for
from app.google_sheets import get_sheet

bp = Blueprint('main', __name__, template_folder='../templates')

@bp.route('/')
def index():
    try:
        sheet = get_sheet()
        dados = sheet.get_all_records()
        return render_template('index.html', dados=dados)
    except Exception as e:
        print(f"Erro ao acessar Google Sheets: {e}")
        return render_template('index.html', dados=[])

@bp.route('/manage_person', methods=['POST'])
def manage_person():
    try:
        sheet = get_sheet()
        dados = sheet.get_all_records()
        nova_pessoa = {campo: request.form[campo] for campo in dados[0].keys()}
        
        # Verifica se o CPF já existe na planilha
        cpfs = [linha["CPF"] for linha in dados if "CPF" in linha]
        if nova_pessoa["CPF"] in cpfs:
            # Atualiza registro existente
            for i, linha in enumerate(dados):
                if linha["CPF"] == nova_pessoa["CPF"]:
                    sheet.update(f"A{i+2}:Z{i+2}", [[nova_pessoa[col] for col in linha.keys()]])
                    break
        else:
            # Adiciona novo registro
            sheet.append_row([nova_pessoa[col] for col in nova_pessoa.keys()])

        return redirect(url_for('main.index'))

    except Exception as e:
        print(f"Erro ao adicionar ou editar pessoa: {e}")
        return redirect(url_for('main.index'))