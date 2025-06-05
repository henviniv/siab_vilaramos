from flask import Blueprint, render_template, request, redirect, url_for
from app.google_sheets import get_sheet

bp = Blueprint('main', __name__, template_folder='../templates')

@bp.route('/', methods=['GET', 'POST'])
def index():
    try:
        sheet = get_sheet()
        dados = sheet.get_all_records()
        query = request.args.get("query", "").strip().lower()
        
        # Filtrar resultados se houver busca
        if query:
            dados = [linha for linha in dados if query in str(linha.get("NOME", "")).lower()
                      or query in str(linha.get("SUS", "")).lower()
                      or query in str(linha.get("CPF", ""))]

        return render_template("index.html", dados=dados)

    except Exception as e:
        print(f"Erro ao acessar Google Sheets: {e}")
        return render_template("index.html", dados=[])

@bp.route('/manage_person', methods=['POST'])
def manage_person():
    try:
        sheet = get_sheet()
        dados = sheet.get_all_records()
        nova_pessoa = {campo: request.form[campo] for campo in dados[0].keys()}
        
        # Verifica se o CPF já existe na planilha
        cpfs = {linha.get("CPF"): i+2 for i, linha in enumerate(dados) if linha.get("CPF")}
        if nova_pessoa["CPF"] in cpfs:
            # Atualiza registro existente
            linha_atualizar = cpfs[nova_pessoa["CPF"]]
            sheet.update(f"A{linha_atualizar}:Z{linha_atualizar}", [[nova_pessoa[col] for col in nova_pessoa.keys()]])
        else:
            # Insere novo registro na linha 3 (logo após o cabeçalho)
            sheet.insert_row([nova_pessoa[col] for col in nova_pessoa.keys()], index=3)

        return redirect(url_for('main.index'))

    except Exception as e:
        print(f"Erro ao adicionar ou editar pessoa: {e}")
        return redirect(url_for('main.index'))

@bp.route('/edit', methods=['GET', 'POST'])
def edit_person():
    try:
        sheet = get_sheet()
        dados = sheet.get_all_records()
        cpf = request.args.get("cpf", "")

        if request.method == 'POST':
            nova_pessoa = {campo: request.form[campo] for campo in dados[0].keys()}
            cpfs = {linha.get("CPF"): i+2 for i, linha in enumerate(dados) if linha.get("CPF")}

            if cpf in cpfs:
                linha_atualizar = cpfs[cpf]
                sheet.update(f"A{linha_atualizar}:Z{linha_atualizar}", [[nova_pessoa[col] for col in nova_pessoa.keys()]])

            return redirect(url_for('main.index'))

        pessoa = next((linha for linha in dados if linha.get("CPF") == cpf), None)
        return render_template("edit.html", pessoa=pessoa)

    except Exception as e:
        print(f"Erro ao editar pessoa: {e}")
        return redirect(url_for('main.index'))

@bp.route('/delete', methods=['GET'])
def delete_person():
    try:
        sheet = get_sheet()
        dados = sheet.get_all_records()
        cpf = request.args.get("cpf", "")

        cpfs = {linha.get("CPF"): i+2 for i, linha in enumerate(dados) if linha.get("CPF")}
        if cpf in cpfs:
            sheet.delete_rows(cpfs[cpf])

        return redirect(url_for('main.index'))

    except Exception as e:
        print(f"Erro ao excluir pessoa: {e}")
        return redirect(url_for('main.index'))