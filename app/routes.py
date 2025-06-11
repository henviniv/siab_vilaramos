from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.auth import User, USERS
from app.google_sheets import get_sheet
import re
import builtins
from string import ascii_uppercase

bp = Blueprint('main', __name__, template_folder='../templates')

COLUNAS_FIXAS = [
    "COR/ETNIA", "NOME", "SUS", "Família", "Data de Nascimento", "idade", "Gênero", "GESTANTE", "DIA",
    "HAS", "HIPERDIA", "INSULINO", "SM", "CPF", "TB", "HAN", "OBESIDADE", "TABAGISTA", "USO DE DROGAS",
    "USO DE ALCOOL", "ACAMADO", "RESTRITO", "ACAMADO/RESTRITO VACINADO", "ASMÁTICO DPOC", "BOLSA FAMÍLIA",
    "AMPI", "USUÁRIOS DE FRALDAS", "E-SUS", "SIGA", "UNIFICAÇÃO", "SIFILIS", "ENDEREÇO"
]


def limpar_cpf(cpf):
    return re.sub(r"\D", "", builtins.str(cpf))

def num_to_col(n):
    result = ""
    while n > 0:
        n, r = divmod(n - 1, 26)
        result = ascii_uppercase[r] + result
    return result

def obter_dados_sheet(sheet):
    return [
        {chave: builtins.str(linha.get(chave, "")) for chave in COLUNAS_FIXAS}
        for linha in sheet.get_all_records()
    ]

@bp.route('/', methods=['GET'])
def index():
    try:
        sheet = get_sheet()
        dados_crus = sheet.get_all_records()
        dados = [{chave: builtins.str(valor) for chave, valor in linha.items()} for linha in dados_crus]

        mostrar_todas = request.args.get("todas") == "1"

        # Detecta todas as colunas reais no sheet
        todas_colunas = []
        for linha in dados:
            for col in linha:
                if col not in todas_colunas:
                    todas_colunas.append(col)

        campos = todas_colunas if mostrar_todas else COLUNAS_FIXAS

        colunas_extras = ['GESTANTE']  # Pode adicionar mais: ['GESTANTE', 'CAMPO_X', 'CAMPO_Y']

        query = request.args.get("query", "").strip().lower()

        if query:
            dados = [linha for linha in dados if query in linha.get("NOME", "").lower()
                     or query in linha.get("SUS", "").lower()
                     or query in linha.get("CPF", "")]

        return render_template("index.html", dados=dados, campos=campos, colunas_extras=colunas_extras,
                               limpar_cpf=limpar_cpf, mostrar_todas=mostrar_todas)

    except Exception as e:
        print(f"[ERRO] Falha ao acessar Google Sheets: {e}")
        return render_template("index.html", dados=[], campos=COLUNAS_FIXAS, colunas_extras=[],
                               mensagem_erro=str(e), mostrar_todas=False)

@bp.route('/create_or_update_person', methods=['POST'])
def create_or_update_person():
    try:
        sheet = get_sheet()
        dados = obter_dados_sheet(sheet)
        campos = list(dados[0].keys()) if dados else COLUNAS_FIXAS

        nova_pessoa = {campo: builtins.str(request.form.get(campo, "")) for campo in campos}
        cpf_bruto = nova_pessoa.get("CPF", "")
        cpf_limpo = limpar_cpf(cpf_bruto)

        if not cpf_limpo:
            print("[AVISO] CPF não informado.")
            return redirect(url_for('main.index'))

        cpfs = {limpar_cpf(linha.get("CPF", "")): i + 2 for i, linha in enumerate(dados) if linha.get("CPF")}
        ultima_col = num_to_col(len(campos))

        if cpf_limpo in cpfs:
            linha_atualizar = cpfs[cpf_limpo]
            sheet.update(f"A{linha_atualizar}:{ultima_col}{linha_atualizar}",
                         [[nova_pessoa.get(col, "") for col in campos]])
            print(f"[INFO] Pessoa com CPF {cpf_limpo} atualizada.")
        else:
            sheet.insert_rows([[nova_pessoa.get(col, "") for col in campos]], row=3)
            print(f"[INFO] Pessoa com CPF {cpf_limpo} inserida na linha 3.")

        return redirect(url_for('main.index'))

    except Exception as e:
        print(f"[ERRO] Falha ao criar/atualizar pessoa: {e}")
        return redirect(url_for('main.index'))


@bp.route('/update_person', methods=['POST'])
def update_person():
    try:
        sheet = get_sheet()
        dados = obter_dados_sheet(sheet)
        campos = list(dados[0].keys()) if dados else COLUNAS_FIXAS

        cpf_param = request.form.get("CPF", "")
        cpf_limpo = limpar_cpf(cpf_param)

        if not cpf_limpo:
            return jsonify({"erro": "CPF inválido"}), 400

        nova_pessoa = {campo: builtins.str(request.form.get(campo, "")) for campo in campos}
        cpfs = {limpar_cpf(linha.get("CPF", "")): i + 2 for i, linha in enumerate(dados) if linha.get("CPF")}

        ultima_col = num_to_col(len(campos))

        if cpf_limpo in cpfs:
            linha_atualizar = cpfs[cpf_limpo]
            sheet.update(f"A{linha_atualizar}:{ultima_col}{linha_atualizar}",
                         [[nova_pessoa.get(col, "") for col in campos]])
            print(f"[INFO] Pessoa com CPF {cpf_limpo} atualizada.")
            return redirect(url_for('main.index'))  # ✅ redirecionar para a tela principal
        else:
            print(f"[AVISO] Pessoa com CPF {cpf_limpo} não encontrada para atualização.")
            return jsonify({"erro": "Pessoa não encontrada"}), 404

    except Exception as e:
        print(f"[ERRO] Falha ao atualizar pessoa: {e}")
        return jsonify({"erro": "Erro interno"}), 500

@bp.route('/delete', methods=['POST'])
def delete_person():
    try:
        sheet = get_sheet()
        dados = obter_dados_sheet(sheet)
        cpf_param = request.form.get("cpf", "")
        cpf_limpo = limpar_cpf(cpf_param)

        if not cpf_limpo:
            print("[AVISO] Nenhum CPF informado para exclusão.")
            return redirect(url_for('main.index'))

        cpfs = {limpar_cpf(linha.get("CPF", "")): i + 2 for i, linha in enumerate(dados) if linha.get("CPF")}

        if cpf_limpo in cpfs:
            sheet.delete_rows(cpfs[cpf_limpo])
            print(f"[INFO] Pessoa com CPF {cpf_limpo} excluída.")
        else:
            print(f"[AVISO] CPF {cpf_limpo} não encontrado para exclusão.")

        return redirect(url_for('main.index'))

    except Exception as e:
        print(f"[ERRO] Falha ao excluir pessoa: {e}")
        return redirect(url_for('main.index'))

@bp.route('/edit', methods=['GET'])
def get_person_data():
    try:
        sheet = get_sheet()
        dados = obter_dados_sheet(sheet)
        cpf = request.args.get("cpf", "")
        cpf_limpo = limpar_cpf(cpf)

        print(f"[DEBUG] CPF recebido: {cpf}")
        print(f"[DEBUG] CPF limpo: {cpf_limpo}")
        print(f"[DEBUG] Total de registros: {len(dados)}")

        if not cpf_limpo:
            return jsonify({"erro": "CPF inválido"}), 400

        for linha in dados:
            print(f"[DEBUG] Verificando linha: {linha.get('CPF', '')}")
            if limpar_cpf(linha.get("CPF", "")) == cpf_limpo:
                print(f"[DEBUG] Pessoa encontrada: {linha}")
                return jsonify(linha)

        print(f"[AVISO] CPF não encontrado para edição: {cpf}")
        return jsonify({"erro": "Pessoa não encontrada"}), 404

    except Exception as e:
        print(f"[ERRO] Falha ao buscar dados da pessoa: {e}")
        return jsonify({"erro": "Erro interno"}), 500

        @bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user_data = USERS.get(username)

        if user_data and user_data['password'] == password:
            user = User(id=username, username=username, role=user_data['role'], aba=user_data['aba'])
            login_user(user)
            flash("Login realizado com sucesso", "success")
            return redirect(url_for('main.index'))

        flash("Usuário ou senha inválidos", "danger")
        return redirect(url_for('main.login'))

    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Você saiu com sucesso", "info")
    return redirect(url_for('main.login'))