import os
import re

from flask import Flask

from app.extensions import login_manager, limiter
from app.auth import User, load_user, auth_bp
from app.routes import bp
from app.ai.routes import ai_bp


def create_app():

    app = Flask(
        __name__,
        static_folder="static",
        template_folder="templates"
    )

    

    app.secret_key = os.getenv("FIRST_SECRET_KEY")

    if not app.secret_key:
        raise RuntimeError(
            "FIRST_SECRET_KEY não configurada."
        )

    

    @app.template_filter("limpar_cpf")
    def limpar_cpf_filter(cpf):

        return re.sub(
            r"\D",
            "",
            cpf or ""
        )

    

    login_manager.init_app(app)

    login_manager.login_view = "auth.login"

    login_manager.user_loader(load_user)

    

    limiter.init_app(app)

    

    app.register_blueprint(bp)

    

    app.register_blueprint(auth_bp)

    

    app.register_blueprint(ai_bp)

    return app