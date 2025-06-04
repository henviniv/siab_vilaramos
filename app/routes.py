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
            dados = [
                linha for linha in dados
                if query in str(linha.get("NOME", "")).lower()
                or query in str(linha.get("SUS", "")).lower()
                or query in str(linha.get("CPF", ""))
            ]

        return render_template("index.html", dados=dados)

    except Exception as e:
        print(f"Erro ao acessar Google Sheets: {e}")
        return render_template("index.html", dados=[])

@bp.route('/manage_person', methods=['POST'])
def manage_person():
    try:
        sheet = get_sheet()
        dados = sheet.get_all_records()
        
        # Coleta os campos da nova pessoa a partir do formulário
        campos = dados[0].keys() if dados else request.form.keys()
        nova_pessoa = {campo: request.form[campo] for campo in campos}

        # Verifica se o CPF já existe na planilha
        cpfs = [linha["CPF"] for linha in dados if "CPF" in linha]
        if nova_pessoa["CPF"] in cpfs:
            # Atualiza registro existente
            for i, linha in enumerate(dados):
                if linha["CPF"] == nova_pessoa["CPF"]:
                    linha_planilha = i + 3  # Ajuste: dados começam na linha 3
                    sheet.update(
                        f"A{linha_planilha}:Z{linha_planilha}",
                        [[nova_pessoa[col] for col in linha.keys()]]
                    )
                    break
        else:
            # Adiciona novo registro na próxima linha disponível a partir da linha 3
            nova_linha = len(dados) + 3
            sheet.update(
                f"A{nova_linha}:Z{nova_linha}",
                [[nova_pessoa[col] for col in nova_pessoa.keys()]]
            )

        return redirect(url_for('main.index'))

    except Exception as e:
        print(f"Erro ao adicionar ou editar pessoa: {e}")
        return redirect(url_for('main.index'))