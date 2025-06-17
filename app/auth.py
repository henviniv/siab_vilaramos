from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin

auth_bp = Blueprint('auth', __name__)
login_manager = LoginManager()

# Classe de usuário para o Flask-Login
class User(UserMixin):
    def __init__(self, id, username, role, aba, planilha):
        self.id = id
        self.username = username
        self.role = role        # "admin" ou "micro"
        self.aba = aba          # Nome da aba no Google Sheets (ex: "MICRO 23")
        self.planilha = planilha  # Nome da planilha (ex: "EQUIPE 4")

# Dicionário de usuários (pode ser substituído por planilha ou banco depois)
USERS = {
    "admin": {
        "password": "Hidek_22",
        "role": "admin",
        "aba": None,
        "planilha": None
    },
    "micro19": {
        "password": "senha19",
        "role": "micro",
        "aba": "MICRO 19",
        "planilha": "EQUIPE 4"
    },
    "micro20": {
        "password": "senha20",
        "role": "micro",
        "aba": "MICRO 20",
        "planilha": "EQUIPE 4"
    },
    "micro21": {
        "password": "senha21",
        "role": "micro",
        "aba": "MICRO 21",
        "planilha": "EQUIPE 4"
    },
    "micro22": {
        "password": "senha22",
        "role": "micro",
        "aba": "MICRO 22",
        "planilha": "EQUIPE 4"
    },
    "micro23": {
        "password": "senha23",
        "role": "micro",
        "aba": "MICRO 23",
        "planilha": "EQUIPE 4"
    },
    "micro24": {
        "password": "senha24",
        "role": "micro",
        "aba": "MICRO 24",
        "planilha": "EQUIPE 4"
    }
}

@login_manager.user_loader
def load_user(user_id):
    user_data = USERS.get(user_id)
    if user_data:
        return User(
            id=user_id,
            username=user_id,
            role=user_data["role"],
            aba=user_data["aba"],
            planilha=user_data["planilha"]
        )
    return None

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        senha = request.form['password']
        user_data = USERS.get(username)

        if user_data and senha == user_data['password']:
            user = User(
                id=username,
                username=username,
                role=user_data['role'],
                aba=user_data['aba'],
                planilha=user_data['planilha']
            )
            login_user(user)
            return redirect(url_for('main.index'))
        else:
            flash("Usuário ou senha inválidos", "error")
            return render_template('login.html')

    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
