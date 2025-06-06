from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from app.google_sheets import get_sheet
import re
import builtins  # Para garantir que str seja corretamente referenciado
from string import ascii_uppercase

bp = Blueprint('main', __name__, template_folder='../templates')

# Lista fixa de colunas
COLUNAS_FIXAS = [
    "COR/ETNIA", "NOME", "SUS", "Família", "Data de Nascimento", "idade", "Gênero", "GESTANTE", "DIA",
    "HAS", "HIPERDIA", "INSULINO", "SM", "CPF", "TB", "HAN", "OBESIDADE", "TABAGISTA", "USO DE DROGAS",
    "USO DE ALCOOL", "ACAMADO", "RESTRITO", "ACAMADO/RESTRITO VACINADO", "ASMÁTICO DPOC", "BOLSA FAMÍLIA",
    "AMPI", "USUÁRIOS DE FRALDAS", "E-SUS", "SIGA", "UNIFICAÇÃO", "SIFILIS", "ENDEREÇO"
]

def limpar_cpf(cpf):
    return re.sub(r"\D", "", builtins.str(cpf))

def num_to_col(n):
    """Converte número para letra de coluna do Excel (1->A, 27->AA)"""
    result = ""
    while n > 0:
        n, r = divmod(n-1, 26)
        result = ascii_uppercase[r] + result
    return result

@bp.route('/', methods=['GET'])
def index():
    try:
        sheet = get_sheet()
        dados = [
            {chave: builtins.str(linha.get(chave, "")) for chave in COLUNAS_FIXAS}
            for linha in sheet.get_all_records()
        ]
        query = request.args.get("query", "").strip().lower()

        if query:
            dados = [linha for linha in dados if query in linha.get("NOME", "").lower()
                     or query in linha.get("SUS", "").lower()
                     or query in linha.get("CPF", "")]

        campos = list(dados[0].keys()) if dados else COLUNAS_FIXAS

        return render_template("index.html", dados=dados, campos=campos, limpar_cpf=limpar_cpf)

    except Exception as e:
        print(f"Erro ao acessar Google Sheets: {e}")
        return render_template("index.html", dados=[], campos=COLUNAS_FIXAS)

@bp.route('/manage_person', methods=['POST'])
def manage_person():
    try:
        sheet = get_sheet()
        dados = [
            {chave: builtins.str(linha.get(chave, "")) for chave in COLUNAS_FIXAS}
            for linha in sheet.get_all_records()
        ]
        campos = list(dados[0].keys()) if dados else COLUNAS_FIXAS

        nova_pessoa = {campo: builtins.str(request.form.get(campo, "")) for campo in campos}
        cpf_limpo = limpar_cpf(nova_pessoa.get("CPF", ""))

        cpfs = {limpar_cpf(linha.get("CPF", "")): i + 2 for i, linha in enumerate(dados) if linha.get("CPF")}

        ultima_col = num_to_col(len(campos))

        if cpf_limpo in cpfs:
            linha_atualizar = cpfs[cpf_limpo]
            sheet.update(f"A{linha_atualizar}:{ultima_col}{linha_atualizar}",
                         [[nova_pessoa.get(col, "") for col in campos]])
        else:
            sheet.insert_row([nova_pessoa.get(col, "") for col in campos], index=3)

        return redirect(url_for('main.index'))

    except Exception as e:
        print(f"Erro ao adicionar ou editar pessoa: {e}")
        return redirect(url_for('main.index'))

@bp.route('/edit', methods=['GET'])
def get_person_data():
    try:
        sheet = get_sheet()
        dados = [
            {chave: builtins.str(linha.get(chave, "")) for chave in COLUNAS_FIXAS}
            for linha in sheet.get_all_records()
        ]
        cpf = request.args.get("cpf", "")
        cpf_limpo = limpar_cpf(cpf)

        pessoa = next((linha for linha in dados if limpar_cpf(linha.get("CPF", "")) == cpf_limpo), None)

        if pessoa:
            return jsonify(pessoa)
        return jsonify({"erro": "Pessoa não encontrada"}), 404
    except Exception as e:
        print(f"Erro ao buscar pessoa para edição: {e}")
        return jsonify({"erro": "Erro interno"}), 500

@bp.route('/update_person', methods=['POST'])
def update_person():
    try:
        sheet = get_sheet()
        dados = [
            {chave: builtins.str(linha.get(chave, "")) for chave in COLUNAS_FIXAS}
            for linha in sheet.get_all_records()
        ]
        campos = list(dados[0].keys()) if dados else COLUNAS_FIXAS

        cpf_param = request.args.get("cpf", "") or request.form.get("CPF", "")
        cpf_limpo = limpar_cpf(cpf_param)

        nova_pessoa = {campo: builtins.str(request.form.get(campo, "")) for campo in campos}

        cpfs = {limpar_cpf(linha.get("CPF", "")): i + 2 for i, linha in enumerate(dados) if linha.get("CPF")}

        ultima_col = num_to_col(len(campos))

        if cpf_limpo in cpfs:
            linha_atualizar = cpfs[cpf_limpo]
            sheet.update(f"A{linha_atualizar}:{ultima_col}{linha_atualizar}",
                         [[nova_pessoa.get(col, "") for col in campos]])
            return jsonify({"sucesso": True})
        else:
            return jsonify({"erro": "Pessoa não encontrada"}), 404

    except Exception as e:
        print(f"Erro ao atualizar pessoa: {e}")
        return jsonify({"erro": "Erro interno"}), 500

@bp.route('/delete', methods=['GET'])
def delete_person():
    try:
        sheet = get_sheet()
        dados = [
            {chave: builtins.str(linha.get(chave, "")) for chave in COLUNAS_FIXAS}
            for linha in sheet.get_all_records()
        ]
        cpf_param = request.args.get("cpf", "")
        cpf_param = limpar_cpf(cpf_param)

        cpfs = {limpar_cpf(linha.get("CPF", "")): i + 2 for i, linha in enumerate(dados) if linha.get("CPF")}

        if cpf_param in cpfs:
            sheet.delete_rows(cpfs[cpf_param])

        return redirect(url_for('main.index'))

    except Exception as e:
        print(f"Erro ao excluir pessoa: {e}")
        return redirect(url_for('main.index'))
