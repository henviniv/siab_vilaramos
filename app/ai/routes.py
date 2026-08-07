from flask import Blueprint, jsonify, render_template, request
from flask_login import current_user, login_required

from app.ai.chat import perguntar


ai_bp = Blueprint(
    "ai",
    __name__,
    url_prefix="/ia"
)


@ai_bp.route("/", methods=["GET", "POST"])
def chat():

    resposta = None

    if request.method == "POST":

        pergunta = request.form.get("pergunta", "").strip()

        if pergunta:
            resposta = perguntar(pergunta)

    return render_template(
        "ia/chat.html",
        resposta=resposta
    )

@ai_bp.route("/perguntar", methods=["POST"])
@login_required
def perguntar_json():
    dados = request.get_json(silent=True) or {}
    pergunta = str(dados.get("pergunta", "")).strip()

    if not pergunta:
        return jsonify({
            "success": False,
            "message": "Digite uma pergunta para o assistente.",
        }), 400

    try:
        resposta = perguntar(pergunta, usuario=current_user)
    except ValueError as erro:
        return jsonify({
            "success": False,
            "message": str(erro),
        }), 400
    except Exception:
        return jsonify({
            "success": False,
            "message": "Não foi possível consultar a IA agora. Tente novamente em instantes.",
        }), 500

    return jsonify({
        "success": True,
        "resposta": resposta,
    })
