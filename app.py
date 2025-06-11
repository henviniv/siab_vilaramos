from flask import Flask
from app.routes import bp
from flask_login import LoginManager
from app.auth import User, USERS  # importa a classe e os usuários

# Criando a aplicação Flask com caminhos explícitos
app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'Hidek_22'  # 🔐 Adicione sua chave aqui
app.register_blueprint(bp) # Se tiver Blueprints:

if __name__ == '__main__':
    app.run(debug=True)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'main.login'  # redireciona se não estiver logado

@login_manager.user_loader
def load_user(user_id):
    for username, data in USERS.items():
        if username == user_id:
            return User(id=user_id, username=username, role=data["role"], aba=data["aba"])
    return None