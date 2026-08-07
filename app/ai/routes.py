from flask import Blueprint, render_template, request

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