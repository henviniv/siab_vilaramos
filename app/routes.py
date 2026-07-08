from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session, flash, request, send_file, Flask
from flask_login import login_user, logout_user, login_required, current_user
from app.google_sheets import get_sheet
from app.auth import USERS, User
import re
import builtins
import unicodedata
from string import ascii_uppercase
from fpdf import FPDF
from datetime import datetime
from flask import send_file, request
from io import BytesIO
from app.database import buscar_micro
from app.supabase_db import supabase
from app.fechamentos import gerar_fechamento_micro
from app.familias_vagas import (
    encontrar_familias_vagas,
    obter_numero_micro
)

bp = Blueprint('main', __name__, template_folder='../templates')

bp_listas = Blueprint('listas', __name__, template_folder='../templates')

def limpar_cpf(cpf):
    return re.sub(r"\D", "", builtins.str(cpf))


def normalizar_texto_busca(valor):
    texto = builtins.str(valor or "").strip().lower()
    texto_sem_acentos = unicodedata.normalize("NFKD", texto).encode("ASCII", "ignore").decode("ASCII")
    return re.sub(r"\s+", " ", texto_sem_acentos)


def somente_digitos(valor):
    return re.sub(r"\D", "", builtins.str(valor or ""))


def num_to_col(n):
    result = ""
    while n > 0:
        n, r = divmod(n - 1, 26)
        result = ascii_uppercase[r] + result
    return result


@bp.route('/', methods=['GET'])
@login_required
def index():

    if current_user.is_authenticated and current_user.role == "admin" and not request.args.get("query"):
        return redirect(url_for("main.painel_admin"))

    try:
        print(f"[DEBUG] Usuário: {current_user.username}, aba: {current_user.aba}")

        # Busca diretamente do Supabase
        dados_crus = buscar_micro(
            current_user.planilha,
            current_user.aba
        )

        # Converte todos os valores para string
        dados = []
        for linha in dados_crus:
            dados.append({
                chave: "" if valor is None else str(valor)
                for chave, valor in linha.items()
            })

        # Ordenação
        dados.sort(key=lambda x: x.get("familia", ""))

        # Colunas dinâmicas
        mostrar_todas = True
        todas_colunas = []

        for linha in dados:
            for col in linha:
                if col not in todas_colunas:
                    todas_colunas.append(col)

        campos = todas_colunas
        colunas_extras = []

        # Busca
        query = request.args.get("query", "").strip().lower()

        if query:
            dados = [
                linha for linha in dados
                if query in linha.get("nome", "").lower()
                or query in linha.get("endereco", "").lower()
            ]

        # Famílias vagas
        micro_numero = obter_numero_micro(current_user.aba)

        familias_existentes = []

        for linha in dados_crus:
            familia = linha.get("familia")
            if familia:
                familias_existentes.append(str(familia))

        vagas = encontrar_familias_vagas(
            familias_existentes,
            micro_numero
        )

        proxima_familia = vagas[0] if vagas else None

        return render_template(
            "index.html",
            dados=dados,
            campos=campos,
            colunas_extras=colunas_extras,
            limpar_cpf=limpar_cpf,
            mostrar_todas=mostrar_todas,
            vagas=vagas,
            proxima_familia=proxima_familia
        )

    except Exception as e:
        print(f"[ERRO] Falha ao acessar Supabase: {e}")

        return render_template(
            "index.html",
            dados=[],
            campos=[],
            colunas_extras=[],
            mensagem_erro=str(e),
            mostrar_todas=True,
            vagas=[],
            proxima_familia=None
        )



@bp.route('/create_or_update_person', methods=['POST'])
@login_required
def create_or_update_person():
    try:

        def texto(campo):
            valor = request.form.get(campo, "")
            return str(valor).strip().upper()

        data_nascimento = request.form.get("DATA DE NASCIMENTO", "").strip()

        if data_nascimento:
            try:
                data_nascimento = datetime.strptime(
                    data_nascimento,
                    "%Y-%m-%d"
                ).strftime("%d/%m/%Y")
            except:
                data_nascimento = ""

        pessoa = {
            "equipe": current_user.planilha,
            "micro": current_user.aba,

            "cor_etnia": texto("COR/ETNIA"),
            "nome": texto("NOME"),
            "sus": limpar_cpf(request.form.get("SUS", "")),
            "familia": texto("FAMILIA"),
            "data_nascimento": data_nascimento,
            "idade": "",
            "genero": texto("GENERO"),
            "gestante": texto("GESTANTE"),
            "dia": texto("DIA"),
            "has": texto("HAS"),
            "hiperdia": texto("HIPERDIA"),
            "insulino": texto("INSULINO"),
            "sm": texto("SM"),
            "cpf": limpar_cpf(request.form.get("CPF", "")),
            "tb": texto("TB"),
            "han": texto("HAN"),
            "obesa": texto("OBESA"),
            "tabagista": texto("TABAGISTA"),
            "uso_de_drogas": texto("USO DE DROGAS"),
            "uso_de_alcool": texto("USO DE ALCOOL"),
            "acamado": texto("ACAMADO"),
            "restrito": texto("RESTRITO"),
            "asmatico_dpoc": texto("ASMÁTICO DPOC"),
            "bolsa_familia": texto("BOLSA FAMÍLIA"),
            "ampi": texto("AMPI"),
            "fralda": texto("FRALDA"),
            "sifilis": texto("SIFILIS"),
            "endereco": texto("ENDEREÇO"),
        }

        # Procura pelo CPF
        if pessoa["cpf"]:

            resultado = (
                supabase
                .table("pessoas")
                .select("id")
                .eq("cpf", pessoa["cpf"])
                .eq("micro", current_user.aba)
                .execute()
            )

            if resultado.data:
                (
                    supabase
                    .table("pessoas")
                    .update(pessoa)
                    .eq("id", resultado.data[0]["id"])
                    .execute()
                )

                flash("Pessoa atualizada com sucesso.", "success")
                return redirect(url_for("main.index"))

        # Procura pelo nome
        resultado = (
            supabase
            .table("pessoas")
            .select("id")
            .eq("nome", pessoa["nome"])
            .eq("micro", current_user.aba)
            .execute()
        )

        if resultado.data:

            (
                supabase
                .table("pessoas")
                .update(pessoa)
                .eq("id", resultado.data[0]["id"])
                .execute()
            )

            flash("Pessoa atualizada com sucesso.", "success")

        else:

            (
                supabase
                .table("pessoas")
                .insert(pessoa)
                .execute()
            )

            flash("Pessoa cadastrada com sucesso.", "success")

        return redirect(url_for("main.index"))

    except Exception as e:
        print(e)
        flash("Erro ao salvar.", "danger")
        return redirect(url_for("main.index"))




@bp.route('/update_person', methods=['POST'])
@login_required
def update_person():
    try:

        nome_original = request.args.get("nome", "").strip().upper()

        if not nome_original:
            return jsonify({"erro": "Nome inválido"}), 400

        def texto(campo):
            valor = request.form.get(campo, "")
            return str(valor).strip().upper()

        data_nascimento = request.form.get("DATA DE NASCIMENTO", "").strip()

        if data_nascimento:
            try:
                data_nascimento = datetime.strptime(
                    data_nascimento,
                    "%Y-%m-%d"
                ).strftime("%d/%m/%Y")
            except:
                data_nascimento = ""

        pessoa = {
            "cor_etnia": texto("COR/ETNIA"),
            "nome": texto("NOME"),
            "sus": limpar_cpf(request.form.get("SUS", "")),
            "familia": texto("FAMILIA"),
            "data_nascimento": data_nascimento,
            "idade": "",
            "genero": texto("GENERO"),
            "gestante": texto("GESTANTE"),
            "dia": texto("DIA"),
            "has": texto("HAS"),
            "hiperdia": texto("HIPERDIA"),
            "insulino": texto("INSULINO"),
            "sm": texto("SM"),
            "cpf": limpar_cpf(request.form.get("CPF", "")),
            "tb": texto("TB"),
            "han": texto("HAN"),
            "obesa": texto("OBESA"),
            "tabagista": texto("TABAGISTA"),
            "uso_de_drogas": texto("USO DE DROGAS"),
            "uso_de_alcool": texto("USO DE ALCOOL"),
            "acamado": texto("ACAMADO"),
            "restrito": texto("RESTRITO"),
            "asmatico_dpoc": texto("ASMÁTICO DPOC"),
            "bolsa_familia": texto("BOLSA FAMÍLIA"),
            "ampi": texto("AMPI"),
            "fralda": texto("FRALDA"),
            "sifilis": texto("SIFILIS"),
            "endereco": texto("ENDEREÇO"),
        }

        resultado = (
            supabase
            .table("pessoas")
            .select("id")
            .eq("nome", nome_original)
            .eq("micro", current_user.aba)
            .execute()
        )

        if not resultado.data:
            return jsonify({"erro": "Pessoa não encontrada"}), 404

        (
            supabase
            .table("pessoas")
            .update(pessoa)
            .eq("id", resultado.data[0]["id"])
            .execute()
        )

        return redirect(url_for("main.index"))

    except Exception as e:
        print(f"[ERRO] {e}")
        return jsonify({"erro": "Erro interno"}), 500




@bp.route('/delete', methods=['POST'])
@login_required
def delete_person():
    try:

        nome = request.form.get("nome", "").strip().upper()

        if not nome:
            flash("Nome inválido para exclusão.", "warning")
            return redirect(url_for('main.index'))

        # Procura a pessoa no Supabase pelo nome e micro
        resultado = (
            supabase
            .table("pessoas")
            .select("id")
            .eq("nome", nome)
            .eq("micro", current_user.aba)
            .execute()
        )

        if not resultado.data:
            flash("Pessoa não encontrada para exclusão.", "warning")
            return redirect(url_for('main.index'))

        # Exclui usando o id encontrado
        (
            supabase
            .table("pessoas")
            .delete()
            .eq("id", resultado.data[0]["id"])
            .execute()
        )

        print(f"[INFO] Pessoa com NOME {nome} excluída.")

        flash("Pessoa excluída com sucesso.", "success")

        return redirect(url_for('main.index'))

    except Exception as e:
        print(f"[ERRO] Falha ao excluir pessoa: {e}")
        flash("Erro ao excluir pessoa.", "danger")
        return redirect(url_for('main.index'))



@bp.route('/edit', methods=['GET'])
@login_required
def get_person_data():
    try:

        nome = request.args.get("nome", "").strip().upper()

        if not nome:
            return jsonify({"erro": "Nome inválido"}), 400

        resultado = (
            supabase
            .table("pessoas")
            .select("*")
            .eq("nome", nome)
            .eq("micro", current_user.aba)
            .execute()
        )

        if not resultado.data:
            return jsonify({"erro": "Pessoa não encontrada"}), 404

        return jsonify(resultado.data[0])

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

        # ADMIN VÊ TODOS OS FECHAMENTOS
        if current_user.role == "admin":

            from app.auth import USERS

            for usuario, info in USERS.items():

                if info["role"] != "micro":
                    continue

                valores = gerar_fechamento_micro(
                    info["planilha"],
                    info["aba"]
                )

                dados.append({
                    "aba": f"FECHAMENTO {info['aba']}",
                    "equipe": info["planilha"],
                    "valores": valores
                })


        # MICRO VÊ SOMENTE O SEU
        else:

            valores = gerar_fechamento_micro(
                current_user.planilha,
                current_user.aba
            )

            dados.append({
                "aba": f"FECHAMENTO {current_user.aba}",
                "equipe": current_user.planilha,
                "valores": valores
            })


        return render_template(
            "fechamento.html",
            dados=dados
        )


    except Exception as e:

        print(f"[ERRO] Falha ao gerar fechamento: {e}")

        flash(
            "Erro ao gerar fechamento.",
            "danger"
        )

        return redirect(
            url_for("main.index")
        )

@bp.route('/admin/fechamento/<micro_id>')
@login_required
def fechamento_admin(micro_id):

    if current_user.role != "admin":
        flash(
            "Acesso restrito ao administrador.",
            "danger"
        )
        return redirect(url_for("main.index"))


    from app.auth import USERS


    user_info = USERS.get(micro_id)


    if not user_info:

        flash(
            "Micro não encontrada.",
            "warning"
        )

        return redirect(
            url_for("main.painel_admin")
        )


    try:

        valores = gerar_fechamento_micro(
            user_info["planilha"],
            user_info["aba"]
        )


        dados = [{
            "aba": f"FECHAMENTO {user_info['aba']}",
            "equipe": user_info["planilha"],
            "valores": valores
        }]


        return render_template(
            "fechamento.html",
            dados=dados
        )


    except Exception as e:

        print(
            f"[ERRO] Falha ao gerar fechamento admin: {e}"
        )


        flash(
            "Erro ao gerar fechamento.",
            "danger"
        )


        return redirect(
            url_for(
                "main.visualizar_micro",
                micro_id=micro_id
            )
        )

@bp.route('/admin')
@login_required
def painel_admin():
    if current_user.role != "admin":
        flash("Acesso restrito ao administrador.", "danger")
        return redirect(url_for("main.index"))

    from app.auth import USERS

    lista_usuarios = {
        username: info
        for username, info in USERS.items()
        if info["role"] == "micro"
    }

    return render_template(
        "painel_admin.html",
        lista_usuarios=lista_usuarios,
        termo_pesquisa="",
        resultados_pesquisa=[],
        pesquisa_realizada=False,
    )


@bp.route('/admin/pesquisar_usuarios', methods=['GET'])
@login_required
def pesquisar_usuarios_admin():

    if current_user.role != "admin":
        flash("Acesso restrito ao administrador.", "danger")
        return redirect(url_for("main.index"))

    termo_original = request.args.get("q", "").strip()
    termo_normalizado = normalizar_texto_busca(termo_original)

    resultados = []

    if termo_normalizado:

        try:

            resposta = (
                supabase
                .table("pessoas")
                .select("*")
                .execute()
            )

            dados = resposta.data

            for linha in dados:

                nome = str(linha.get("nome", "")).strip()
                familia = str(linha.get("familia", "")).strip()

                nome_normalizado = normalizar_texto_busca(nome)
                familia_normalizada = normalizar_texto_busca(familia)

                if (
                    termo_normalizado in nome_normalizado
                    or termo_normalizado in familia_normalizada
                ):

                    resultados.append({

                        "nome": nome,

                        "familia": linha.get(
                            "familia",
                            ""
                        ),

                        "data_nascimento": linha.get(
                            "data_nascimento",
                            ""
                        ),

                        "idade": linha.get(
                            "idade",
                            ""
                        ),

                        "sus": linha.get(
                            "sus",
                            ""
                        ),

                        "endereco": linha.get(
                            "endereco",
                            ""
                        )
                    })


        except Exception as e:

            print(
                f"[ERRO PESQUISA SUPABASE] {e}"
            )


    resultados.sort(
        key=lambda x: x["nome"]
    )


    lista_usuarios = {
        username: info
        for username, info in USERS.items()
        if info["role"] == "micro"
    }


    return render_template(
        "painel_admin.html",
        lista_usuarios=lista_usuarios,
        termo_pesquisa=termo_original,
        resultados_pesquisa=resultados,
        pesquisa_realizada=True,
    )

@bp.route('/admin/micro/<micro_id>')
@login_required
def visualizar_micro(micro_id):

    if current_user.role != "admin":
        flash(
            "Acesso restrito ao administrador.",
            "danger"
        )
        return redirect(url_for("main.index"))


    user_info = USERS.get(micro_id)

    if not user_info:
        flash(
            "Micro não encontrada.",
            "warning"
        )
        return redirect(
            url_for("main.painel_admin")
        )


    session["micro"] = micro_id


    try:

        resultado = (
            supabase
            .table("pessoas")
            .select("*")
            .eq(
                "equipe",
                user_info["planilha"]
            )
            .eq(
                "micro",
                user_info["aba"]
            )
            .execute()
        )


        dados_crus = resultado.data


        dados = [
            {
                chave: "" if valor is None else str(valor)
                for chave, valor in linha.items()
            }
            for linha in dados_crus
        ]


        campos = (
            list(dados[0].keys())
            if dados
            else []
        )


        return render_template(
            "index.html",
            dados=dados,
            campos=campos,
            colunas_extras=[],
            limpar_cpf=limpar_cpf,
            mostrar_todas=True
        )


    except Exception as e:

        print(
            f"[ERRO] Falha ao acessar micro {micro_id}: {e}"
        )

        flash(
            "Erro ao carregar dados da micro.",
            "danger"
        )

        return redirect(
            url_for("main.painel_admin")
        )
    

@bp.route("/gerar_filipetas", methods=["POST"])
def gerar_filipetas():

    nomes = request.json.get("nomes", [])
    familias = request.json.get("familias", [])
    grupo = request.json.get("grupo", "")
    data_iso = request.json.get("data", "")
    local = request.json.get("local", "")
    hora = request.json.get("hora", "")
    opcao = request.json.get("opcao", "")
    trazer = request.json.get("trazer", "")

    
    data_formatada = "__/__/__"
    if data_iso:
        try:
            data_formatada = datetime.strptime(data_iso, "%Y-%m-%d").strftime("%d/%m/%Y")
        except ValueError:
            pass  

    hora_formatada = hora if hora else "__:__"

    pdf = FPDF()
    pdf.set_auto_page_break(auto=False)
    pdf.add_page()

    largura_filipeta = 90
    altura_filipeta = 80
    margem_esquerda = 10
    margem_topo = 10
    espacamento_horizontal = 10
    espacamento_vertical = 10

    for i, (nome, familia) in enumerate(zip(nomes, familias)):
        idx_na_pagina = i % 6
        linha = idx_na_pagina // 2
        coluna = idx_na_pagina % 2

        x = margem_esquerda + coluna * (largura_filipeta + espacamento_horizontal)
        y = margem_topo + linha * (altura_filipeta + espacamento_vertical)

        if idx_na_pagina == 0 and i != 0:
            pdf.add_page()

        pdf.set_xy(x, y)
        pdf.set_font("Arial", size=12)

        texto = (
            f"{opcao} {grupo}\n\n"
            f"DIA: {data_formatada}  ÀS: {hora_formatada}\n\n"
            f"LOCAL: {local}\n"
            f"CONVOCAÇÃO PARA:\n\n"
            f"{nome.upper()}\n\n"
            f"FAMILIA: {familia.upper()}\n\n"
            f"TRAZER: {trazer}\n"
        )

        pdf.multi_cell(w=largura_filipeta, h=7, txt=texto, border=1)

    file_path = "/tmp/filipetas.pdf"
    pdf.output(file_path)
    return send_file(file_path, as_attachment=False, download_name="filipetas.pdf", mimetype="application/pdf")

@bp.route("/gerar_lista", methods=["POST"])
def gerar_lista():
    dados = request.json.get("dados", [])
    colunas = request.json.get("colunas", [])
    titulo = request.json.get("titulo", "Lista Gerada")
    data_geracao = datetime.now().strftime("%d/%m/%Y %H:%M")

    if not dados or not colunas:
        return jsonify({"error": "Dados ou colunas não fornecidos"}), 400

    pdf = FPDF("L", "mm", "A4")
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.add_page()

    
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, titulo, ln=True, align="C")
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 10, f"Gerado em: {data_geracao}", ln=True, align="C")
    pdf.ln(10)

    
    pdf.set_font("Arial", "B", 10)
    larguras = []
    for coluna in colunas:
        max_len = pdf.get_string_width(coluna) + 6
        for linha in dados:
            valor = str(linha.get(coluna, ""))
            largura_valor = pdf.get_string_width(valor) + 6
            if largura_valor > max_len:
                max_len = largura_valor
        larguras.append(max_len)

    
    largura_total = sum(larguras)
    largura_util = 277
    if largura_total > largura_util:
        fator = largura_util / largura_total
        larguras = [w * fator for w in larguras]

    
    pdf.set_font("Arial", "B", 8)
    for i, coluna in enumerate(colunas):
        pdf.cell(larguras[i], 8, coluna, border=1, align="C")
    pdf.ln()

    
    pdf.set_font("Arial", "", 7)
    for linha in dados:
        for i, coluna in enumerate(colunas):
            valor = str(linha.get(coluna, ""))
            pdf.cell(larguras[i], 6, valor, border=1)
        pdf.ln()

    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="lista.pdf", mimetype="application/pdf")

@bp.route('/fechamento_geral')
def fechamento_geral():
    planilha = request.args.get('planilha', 'CONSOLIDADO GERAL')
    aba = request.args.get('aba')

    worksheet = get_sheet(planilha, aba)
    valores = worksheet.get_all_values()  

    return render_template('fechamento_geral.html', valores=valores, aba=aba)

app = Flask(__name__)

@app.before_request
def force_https():
    if request.headers.get("X-Forwarded-Proto") == "http":
        return redirect(request.url.replace("http://", "https://"), code=301)

@bp.route("/familias_vagas")
@login_required
def familias_vagas():

    # 🔹 pega a planilha corretamente
    sheet = get_sheet(planilha=current_user.planilha, aba=current_user.aba)
    dados_crus = sheet.get_all_records()

    # 🔹 extrai famílias (com e sem acento)
    familias_existentes = []
    for linha in dados_crus:
        familia = linha.get("FAMÍLIA") or linha.get("FAMILIA")
        if familia:
            familias_existentes.append(str(familia))

    # 🔹 pega número da micro
    micro_numero = obter_numero_micro(current_user.aba)

    # 🔹 calcula vagas
    vagas = encontrar_familias_vagas(familias_existentes, micro_numero)

    return render_template("familias_vagas.html", vagas=vagas)
