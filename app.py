from flask import Flask

# Criando a aplicação Flask com caminhos explícitos
app = Flask(__name__, template_folder='templates', static_folder='static')

# Se tiver Blueprints:
from app.routes import bp
app.register_blueprint(bp)

if __name__ == '__main__':
    app.run(debug=True)
