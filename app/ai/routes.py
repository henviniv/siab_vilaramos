from flask import (
    Blueprint,
    jsonify,
    render_template,
    request,
    send_file,
)

from flask_login import current_user, login_required

from app.ai.chat import perguntar, consultar, pediu_exportacao
from app.ai.excel import exportar_excel


ai_bp = Blueprint(
    "ai",
    __name__,
    url_prefix="/ia"
)


@ai_bp.route("/", methods=["GET", "POST"])
@login_required
def chat():

    resposta = None

    if request.method == "POST":

        pergunta = request.form.get("pergunta", "").strip()

        if pergunta:
            resposta = perguntar(
                pergunta,
                usuario=current_user
            )

    return render_template(
        "ia/chat.html",
        resposta=resposta
    )


@ai_bp.route("/perguntar", methods=["POST"])
@login_required
def perguntar_json():

    dados_requisicao = request.get_json(silent=True) or {}

    pergunta = str(
        dados_requisicao.get("pergunta", "")
    ).strip()

    if not pergunta:
        return jsonify({
            "success": False,
            "message": "Digite uma pergunta para o assistente.",
        }), 400

    try:

        resultado = consultar(
            pergunta,
            usuario=current_user
        )

    except ValueError as erro:

        return jsonify({
            "success": False,
            "message": str(erro),
        }), 400

    except Exception as erro:

        print("ERRO IA:", erro)

        return jsonify({
            "success": False,
            "message": (
                "Não foi possível consultar a IA agora. "
                "Tente novamente em instantes."
            ),
        }), 500

    return jsonify({
        "success": True,
        "resposta": resultado["resposta"],
        "dados": resultado["dados"],
        "sql": resultado["sql"],
        "pergunta": resultado["pergunta"],
        "exportar": pediu_exportacao(pergunta),
    })


@ai_bp.route("/exportar", methods=["POST"])
@login_required
def exportar():

    dados_requisicao = request.get_json(silent=True) or {}

    dados = dados_requisicao.get("dados") or []

    if not dados:
        return jsonify({
            "success": False,
            "message": "Nenhum dado disponível para exportação.",
        }), 400

    try:

        # Usa os dados já retornados pela consulta original, evitando
        # nova chamada ao banco ou à IA apenas para gerar o arquivo.
        if not dados:
            return jsonify({
                "success": False,
                "message": "A consulta não encontrou nenhum registro.",
            }), 404

        nome_arquivo = "lista_siab.xlsx"

        caminho = exportar_excel(
            dados,
            nome_arquivo
        )

        return send_file(
            caminho,
            as_attachment=True,
            download_name=nome_arquivo,
            mimetype=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            )
        )

    except ValueError as erro:

        return jsonify({
            "success": False,
            "message": str(erro),
        }), 400

    except Exception as erro:

        print("ERRO EXPORTAÇÃO:", erro)

        return jsonify({
            "success": False,
            "message": (
                "Não foi possível gerar o Excel."
            ),
        }), 500