from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session, flash, request, send_file
from flask_login import login_user, logout_user, login_required, current_user
from app.google_sheets import get_sheet
from app.auth import USERS, User
import re
import builtins
from string import ascii_uppercase
from fpdf import FPDF
from datetime import datetime

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
    if current_user.is_authenticated and current_user.role == "admin" and not request.args.get("query"):
        return redirect(url_for("main.painel_admin"))

    try:
        print(f"[DEBUG] Usuário: {current_user.username}, aba: {current_user.aba}")

       # if not current_user.aba or not current_user.planilha:
           # flash("Nenhuma aba ou planilha associada ao usuário.", "danger")
           # return redirect(url_for("main.logout"))

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
    if current_user.role != "admin" and not current_user.fechamento:
        flash("Acesso não autorizado", "danger")
        return redirect(url_for("main.index"))

    try:
        dados = []

        if current_user.role == "admin":
            for equipe in ["EQUIPE 1", "EQUIPE 2", "EQUIPE 3", "EQUIPE 4", "EQUIPE 5"]:
                for i in range(1, 31):
                    aba = f"FECHAMENTO MICRO {i}"
                    try:
                        sheet = get_sheet(equipe, aba)
                        valores = sheet.get_all_values()
                        if valores:
                            dados.append({
                                "aba": aba,
                                "equipe": equipe,
                                "valores": valores
                            })
                    except Exception as e:
                        print(f"[ERRO] {aba} ({equipe}): {e}")
                        continue
        else:
            aba_fechamento = current_user.fechamento
            sheet = get_sheet(current_user.planilha, aba_fechamento)
            valores = sheet.get_all_values()
            dados.append({
                "aba": aba_fechamento,
                "equipe": current_user.planilha,
                "valores": valores
            })

        return render_template("fechamento.html", dados=dados)

    except Exception as e:
        print(f"[ERRO] Falha ao carregar dados: {e}")
        flash("Erro ao carregar dados da planilha.", "danger")
        return redirect(url_for("main.index"))

@bp.route('/admin/fechamento/<micro_id>')
@login_required
def fechamento_admin(micro_id):
    if current_user.role != "admin":
        flash("Acesso restrito ao administrador.", "danger")
        return redirect(url_for("main.index"))

    from app.auth import USERS

    user_info = USERS.get(micro_id)
    if not user_info:
        flash("Micro não encontrada.", "warning")
        return redirect(url_for("main.painel_admin"))

    nome_aba = user_info["aba"]

    # Determina o nome da aba de fechamento com base no nome da aba da micro
    if nome_aba.startswith("MI"):
        aba_fechamento = f"FECHAMENTO {nome_aba}"
    else:
        aba_fechamento = f"FECHAMENTO {nome_aba.upper()}"

    try:
        sheet = get_sheet(user_info["planilha"], aba_fechamento)
        valores = sheet.get_all_values()

        dados = [{
            "aba": aba_fechamento,
            "equipe": user_info["planilha"],
            "valores": valores
        }]

        return render_template("fechamento.html", dados=dados)

    except Exception as e:
        print(f"[ERRO] Falha ao acessar aba de fechamento: {e}")
        flash("Erro ao acessar os dados de fechamento.", "danger")
        return redirect(url_for("main.visualizar_micro", micro_id=micro_id))

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

    from app.auth import USERS

    user_info = USERS.get(micro_id)
    if not user_info:
        flash("Micro não encontrada.", "warning")
        return redirect(url_for("main.painel_admin"))

    session["micro"] = micro_id  # Salva na sessão

    try:
        sheet = get_sheet(user_info["planilha"], user_info["aba"])
        dados_crus = sheet.get_all_records()
        dados = [{chave: str(valor) for chave, valor in linha.items()} for linha in dados_crus]

        campos = list(dados[0].keys()) if dados else []
        return render_template("index.html", dados=dados, campos=campos,
                               colunas_extras=[], limpar_cpf=limpar_cpf, mostrar_todas=True)

    except Exception as e:
        print(f"[ERRO] Falha ao acessar dados da micro {micro_id}: {e}")
        flash("Erro ao carregar dados da micro.", "danger")
        return redirect(url_for("main.painel_admin"))
    

@bp.route("/gerar_filipetas", methods=["POST"])
def gerar_filipetas():

    nomes = request.json.get("nomes", [])
    grupo = request.json.get("grupo")
    data_iso = request.json.get("data")
    data_formatada = datetime.strptime(data_iso, "%Y-%m-%d").strftime("%d-%m-%Y")
    local = request.json.get("local")
    hora = request.json.get("hora")

    pdf = FPDF()
    pdf.set_auto_page_break(auto=False)
    pdf.add_page()

    largura_filipeta = 90
    altura_filipeta = 60
    margem_esquerda = 10
    margem_topo = 10
    espacamento_horizontal = 10
    espacamento_vertical = 10

    for i, nome in enumerate(nomes):
        idx_na_pagina = i % 8  # de 0 a 5
        linha = idx_na_pagina // 2  # 0, 1, 2
        coluna = idx_na_pagina % 2  # 0 ou 1

        x = margem_esquerda + coluna * (largura_filipeta + espacamento_horizontal)
        y = margem_topo + linha * (altura_filipeta + espacamento_vertical)

        if idx_na_pagina == 0 and i != 0:
            pdf.add_page()

        pdf.set_xy(x, y)
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(w=largura_filipeta, h=7,
            txt=(
                f"GRUPO DE: {grupo}\n"
                f"DIA: {data_formatada}  ÀS {hora}\n\n"
                f"LOCAL: {local}\n"
                f"CONVOCAÇÃO PARA\n\n"
                f"{nome.upper()}\n\n"
                f"TRAZER CARTÃO DO SUS"
            ),
            border=1
        )

    file_path = "/tmp/filipetas.pdf"
    pdf.output(file_path)
    return send_file(file_path, as_attachment=False, download_name="filipetas.pdf", mimetype="application/pdf")


