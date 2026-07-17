from flask import Flask
from flask_login import LoginManager
from app.routes import bp
from app.auth import User

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


    # Blueprint principal
    app.register_blueprint(bp)


    # Flask Login
    login_manager.init_app(app)

    login_manager.login_view = 'main.login'


    # Recupera usuário salvo na sessão
    @login_manager.user_loader
    def load_user(user_id):

        info = (
            supabase
            .table("usuarios")
            .select("*")
            .eq("username", user_id)
            .execute()
        )

        if info:

            return User(
                id=user_id,
                username=user_id,
                role=info["role"],
                micro=info.get("micro"),
                equipe=info.get("equipe")
            )

        return None


    return app