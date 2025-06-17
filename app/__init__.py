from flask import Flask
from flask_login import LoginManager
from app.routes import bp
from app.auth import User, USERS  # User e USERS do seu auth.py
import re

login_manager = LoginManager()

def create_app():
    app = Flask(
        __name__,
        static_folder='static',
        template_folder='templates'
    )

    app.secret_key = '77f6345fdced536f3f36e2638e14fedf'  

    # Filtro Jinja para limpar CPF
    @app.template_filter('limpar_cpf')
    def limpar_cpf_filter(cpf):
        return re.sub(r'\D', '', cpf or "")

    app.register_blueprint(bp)

    # Configuração do Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'  # Rota usada para redirecionar se o usuário não estiver logado

    @login_manager.user_loader
    def load_user(user_id):
        if user_id in USERS:
            info = USERS[user_id]
            return User(id=user_id, username=user_id, role=info["role"], aba=info["aba"], planilha=info["planilha"])
        return None

    return app