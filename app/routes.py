from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.auth import User, USERS
from app.google_sheets import get_sheet
import re
import builtins
from string import ascii_uppercase

bp = Blueprint('main', __name__, template_folder='../templates')


def limpar_cpf(cpf):
    return re.sub(r"\D", "", builtins.str(cpf))


def num_to_col(n):
    result = ""
    while n > 0:
        n, r = divmod(n - 1, 26)
        result = ascii_uppercase[r] + result
    return result


@bp.route('/', methods=['GET'])
@login_required
def index():
    # Só verifica o papel se o usuário estiver autenticado (garantido por @login_required)
    if current_user.is_authenticated and current_user.role == "admin":
        return redirect(url_for("main.painel_admin"))

    try:
        print(f"[DEBUG] Usuário: {current_user.username}, aba: {current_user.aba}")

        if not current_user.aba or not current_user.planilha:
            flash("Nenhuma aba ou planilha associada ao usuário.", "danger")
            return redirect(url_for("main.logout"))

        sheet = get_sheet(planilha=current_user.planilha, aba=current_user.aba)
        dados_crus = sheet.get_all_records()
        dados = [{chave: str(valor) for chave, valor in linha.items()} for linha in dados_crus]

        mostrar_todas = True
        todas_colunas = []

        for linha in dados:
            for col in linha:
                if col not in todas_colunas:
                    todas_colunas.append(col)

        campos = todas_colunas
        colunas_extras = []

        query = request.args.get("query", "").strip().lower()
        if query:
            dados = [
                linha for linha in dados if query in linha.get("NOME", "").lower()
                or query in linha.get("SUS", "").lower()
                or query in linha.get("CPF", "")
            ]

        return render_template(
            "index.html",
            dados=dados,
            campos=campos,
            colunas_extras=colunas_extras,
            limpar_cpf=limpar_cpf,
            mostrar_todas=mostrar_todas
        )

    except Exception as e:
        print(f"[ERRO] Falha ao acessar Google Sheets: {e}")
        return render_template("index.html", dados=[], campos=[], colunas_extras=[],
                               mensagem_erro=str(e), mostrar_todas=True)


# Criação ou atualização de pessoa
@bp.route('/create_or_update_person', methods=['POST'])
@login_required
def create_or_update_person():
    try:
        sheet = get_sheet(planilha=current_user.planilha, aba=current_user.aba)
        dados = sheet.get_all_records()

        campos = []
        for linha in dados:
            for col in linha:
                if col not in campos:
                    campos.append(col)

        nova_pessoa = {}
        for campo in campos:
            valor = builtins.str(request.form.get(campo, ""))
            nova_pessoa[campo] = valor.upper() if campo.upper() != "CPF" else valor

        cpf_limpo = limpar_cpf(nova_pessoa.get("CPF", ""))
        if not cpf_limpo:
            flash("CPF não informado ou inválido", "warning")
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
        flash("Erro ao salvar os dados.", "danger")
        return redirect(url_for('main.index'))

# Atualizar pessoa
@bp.route('/update_person', methods=['POST'])
@login_required
def update_person():
    try:
        sheet = get_sheet(planilha=current_user.planilha, aba=current_user.aba)
        dados = sheet.get_all_records()

        campos = []
        for linha in dados:
            for col in linha:
                if col not in campos:
                    campos.append(col)

        cpf_limpo = limpar_cpf(request.form.get("CPF", ""))
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
            return redirect(url_for('main.index'))
        else:
            print(f"[AVISO] Pessoa com CPF {cpf_limpo} não encontrada para atualização.")
            return jsonify({"erro": "Pessoa não encontrada"}), 404

    except Exception as e:
        print(f"[ERRO] Falha ao atualizar pessoa: {e}")
        return jsonify({"erro": "Erro interno"}), 500

# Excluir pessoa
@bp.route('/delete', methods=['POST'])
@login_required
def delete_person():
    try:
        sheet = get_sheet(planilha=current_user.planilha, aba=current_user.aba)
        dados = sheet.get_all_records()

        cpf_limpo = limpar_cpf(request.form.get("cpf", ""))
        if not cpf_limpo:
            flash("CPF inválido para exclusão.", "warning")
            return redirect(url_for('main.index'))

        cpfs = {limpar_cpf(linha.get("CPF", "")): i + 2 for i, linha in enumerate(dados) if linha.get("CPF")}

        if cpf_limpo in cpfs:
            sheet.delete_rows(cpfs[cpf_limpo])
            print(f"[INFO] Pessoa com CPF {cpf_limpo} excluída.")
        else:
            flash("Pessoa não encontrada para exclusão.", "warning")

        return redirect(url_for('main.index'))

    except Exception as e:
        print(f"[ERRO] Falha ao excluir pessoa: {e}")
        flash("Erro ao excluir pessoa.", "danger")
        return redirect(url_for('main.index'))

# Obter dados da pessoa para edição
@bp.route('/edit', methods=['GET'])
@login_required
def get_person_data():
    try:
        sheet = get_sheet(planilha=current_user.planilha, aba=current_user.aba)
        dados = sheet.get_all_records()

        cpf_limpo = limpar_cpf(request.args.get("cpf", ""))
        if not cpf_limpo:
            return jsonify({"erro": "CPF inválido"}), 400

        for linha in dados:
            if limpar_cpf(linha.get("CPF", "")) == cpf_limpo:
                return jsonify(linha)

        return jsonify({"erro": "Pessoa não encontrada"}), 404

    except Exception as e:
        print(f"[ERRO] Falha ao buscar dados da pessoa: {e}")
        return jsonify({"erro": "Erro interno"}), 500

# Login
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user_data = USERS.get(username)
        if user_data and user_data['password'] == password:
            user = User(
                id=username,
                username=username,
                role=user_data['role'],
                aba=user_data['aba'],
                planilha=user_data['planilha']
            )
            login_user(user)
            session["micro"] = user_data["aba"]
            return redirect(url_for('main.index'))
        else:
            flash("Usuário ou senha incorretos", "danger")
            return redirect(url_for('main.login'))

    return render_template("login.html")


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Você saiu com sucesso", "info")
    return redirect(url_for('main.login'))


@bp.route('/fechamento')
@login_required
def fechamento():
    if current_user.role != "admin" and current_user.aba != "MICRO 23":
        flash("Acesso não autorizado", "danger")
        return redirect(url_for("main.index"))

    try:
        sheet = get_sheet("EQUIPE 4", "FECHAMENTO MICRO 23")
        dados = sheet.get_all_values()
        return render_template("fechamento.html", dados=dados)
    except Exception as e:
        print(f"[ERRO] Falha ao carregar aba de fechamento: {e}")
        flash("Erro ao carregar dados da planilha.", "danger")
        return redirect(url_for("main.index"))

@bp.route('/admin')
@login_required
def painel_admin():
    if current_user.role != "admin":
        flash("Acesso restrito ao administrador.", "danger")
        return redirect(url_for("main.index"))

    from app.auth import USERS  # importa USERS diretamente

    # Filtra apenas usuários com role = "micro"
    lista_usuarios = {
        username: info
        for username, info in USERS.items()
        if info["role"] == "micro"
    }

    return render_template("painel_admin.html", lista_usuarios=lista_usuarios)

@bp.route('/admin/micro/<micro_id>')
@login_required
def visualizar_micro(micro_id):
    if current_user.role != "admin":
        flash("Acesso restrito ao administrador.", "danger")
        return redirect(url_for("main.index"))

    from app.auth import USERS  # Importa o dicionário com os usuários

    user_info = USERS.get(micro_id)
    if not user_info:
        flash("Micro não encontrado.", "warning")
        return redirect(url_for("main.painel_admin"))

    try:
        sheet = get_sheet(user_info["planilha"], user_info["aba"])
        dados_crus = sheet.get_all_records()
        dados = [{chave: str(valor) for chave, valor in linha.items()} for linha in dados_crus]

        campos = list(dados[0].keys()) if dados else []
        return render_template("index.html", dados=dados, campos=campos,
                               colunas_extras=[], limpar_cpf=limpar_cpf, mostrar_todas=True)

    except Exception as e:
        print(f"[ERRO] Falha ao acessar dados da micro {micro_id}: {e}")
        flash(f"Erro ao carregar dados da micro {micro_id}.", "danger")
        return redirect(url_for("main.painel_admin"))
