from flask import Flask
from app.routes import bp

def create_app():
    app = Flask(
        __name__,
        static_folder='static',          # pasta onde está style.css
        template_folder='templates'      # pasta onde está index.html
    )
    app.register_blueprint(bp)
    return app