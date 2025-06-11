from flask import Flask
from flask_login import LoginManager
from app.routes import bp
from app.auth import User, USERS

# Cria a aplicação Flask
app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = '77f6345fdced536f3f36e2638e14fedf'  # 🔐 Chave secreta para sessões

# Registra o blueprint
app.register_blueprint(bp)

# Configura o Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'main.login'  # Rota para redirecionar usuários não logados

# Carrega o usuário com base no ID
@login_manager.user_loader
def load_user(user_id):
    user_data = USERS.get(user_id)
    if user_data:
        return User(id=user_id, username=user_id, role=user_data["role"], aba=user_data["aba"])
    return None

# Executa a aplicação
if __name__ == '__main__':
    app.run(debug=True)