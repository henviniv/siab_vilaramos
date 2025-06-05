from flask import Flask
from app.routes import bp
import re

def create_app():
    app = Flask(
        __name__,
        static_folder='static',      # pasta onde está style.css
        template_folder='templates'  # pasta onde está index.html
    )

    # Filtro Jinja para limpar CPF
    @app.template_filter('limpar_cpf')
    def limpar_cpf_filter(cpf):
        return re.sub(r'\D', '', cpf or "")

    app.register_blueprint(bp)

    return app