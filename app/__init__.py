import os
import re
from flask import Flask
from flask_login import LoginManager
from app.routes import bp
from app.auth import User
from app.supabase_db import supabase

login_manager = LoginManager()


def create_app():

    app = Flask(
        __name__,
        static_folder='static',
        template_folder='templates'
    )

    app.secret_key = os.getenv("FIRST_SECRET_KEY")
    if not app.secret_key:
        raise RuntimeError("FIRST_SECRET_KEY não configurada.")

    # Filtro Jinja para limpar CPF
    @app.template_filter('limpar_cpf')
    def limpar_cpf_filter(cpf):
        return re.sub(r'\D', '', cpf or "")


    # Blueprint principal
    app.register_blueprint(bp)


    # Flask Login
    login_manager.init_app(app)

    login_manager.login_view = 'main.login'


    # Recupera usuário salvo na sessão
    @login_manager.user_loader
    def load_user(user_id):

        resposta = (
            supabase
            .table("usuarios")
            .select("username, role, micro, equipe")
            .eq("username", user_id)
            .execute()
        )


        if not resposta.data:
            return None


        info = resposta.data[0]


        return User(
            id=info["username"],
            username=info["username"],
            role=info["role"],
            micro=info.get("micro"),
            equipe=info.get("equipe")
        )


    return app