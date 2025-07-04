from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin

auth_bp = Blueprint('auth', __name__)
login_manager = LoginManager()

# Classe de usuário para o Flask-Login
class User(UserMixin):
    def __init__(self, id, username, role, aba, planilha, fechamento=None):
        self.id = id
        self.username = username
        self.role = role
        self.aba = aba
        self.planilha = planilha
        self.fechamento = fechamento or (f"FECHAMENTO {aba}" if aba else None)

# Dicionário de usuários
USERS = {
    "admin": {
        "password": "Hidek_22",
        "role": "admin",
        "aba": None,
        "planilha": None
    },
    "micro01": {"password": "senha01", "role": "micro", "aba": "MI 01", "planilha": "EQUIPE 1"},
    "micro02": {"password": "senha02", "role": "micro", "aba": "MI 02", "planilha": "EQUIPE 1"},
    "micro03": {"password": "senha03", "role": "micro", "aba": "MI 03", "planilha": "EQUIPE 1"},
    "micro04": {"password": "senha04", "role": "micro", "aba": "MI 04", "planilha": "EQUIPE 1"},
    "micro05": {"password": "senha05", "role": "micro", "aba": "MI 05", "planilha": "EQUIPE 1"},
    "micro06": {"password": "senha06", "role": "micro", "aba": "MI 06", "planilha": "EQUIPE 1"},
    "micro07": {"password": "senha07", "role": "micro", "aba": "MICRO 7", "planilha": "EQUIPE 2"},
    "micro08": {"password": "senha08", "role": "micro", "aba": "MICRO 8", "planilha": "EQUIPE 2"},
    "micro09": {"password": "senha09", "role": "micro", "aba": "MICRO 9", "planilha": "EQUIPE 2"},
    "micro10": {"password": "senha10", "role": "micro", "aba": "MICRO 10", "planilha": "EQUIPE 2"},
    "micro11": {"password": "senha11", "role": "micro", "aba": "MICRO 11", "planilha": "EQUIPE 2"},
    "micro12": {"password": "senha12", "role": "micro", "aba": "MICRO 12", "planilha": "EQUIPE 2"},
    "micro13": {"password": "senha13", "role": "micro", "aba": "MICRO 13", "planilha": "EQUIPE 3"},
    "micro14": {"password": "senha14", "role": "micro", "aba": "MICRO 14", "planilha": "EQUIPE 3"},
    "micro15": {"password": "senha15", "role": "micro", "aba": "MICRO 15", "planilha": "EQUIPE 3"},
    "micro16": {"password": "senha16", "role": "micro", "aba": "MICRO 16", "planilha": "EQUIPE 3"},
    "micro17": {"password": "senha17", "role": "micro", "aba": "MICRO 17", "planilha": "EQUIPE 3"},
    "micro18": {"password": "senha18", "role": "micro", "aba": "MICRO 18", "planilha": "EQUIPE 3"},
    "micro19": {"password": "senha19", "role": "micro", "aba": "MICRO 19", "planilha": "EQUIPE 4"},
    "micro20": {"password": "senha20", "role": "micro", "aba": "MICRO 20", "planilha": "EQUIPE 4"},
    "micro21": {"password": "senha21", "role": "micro", "aba": "MICRO 21", "planilha": "EQUIPE 4"},
    "micro22": {"password": "senha22", "role": "micro", "aba": "MICRO 22", "planilha": "EQUIPE 4"},
    "micro23": {"password": "senha23", "role": "micro", "aba": "MICRO 23", "planilha": "EQUIPE 4"},
    "micro24": {"password": "senha24", "role": "micro", "aba": "MICRO 24", "planilha": "EQUIPE 4"},
    "micro25": {"password": "senha25", "role": "micro", "aba": "MICRO 25", "planilha": "EQUIPE 5"},
    "micro26": {"password": "senha26", "role": "micro", "aba": "MICRO 26", "planilha": "EQUIPE 5"},
    "micro27": {"password": "senha27", "role": "micro", "aba": "MICRO 27", "planilha": "EQUIPE 5"},
    "micro28": {"password": "senha28", "role": "micro", "aba": "MICRO 28", "planilha": "EQUIPE 5"},
    "micro29": {"password": "senha29", "role": "micro", "aba": "MICRO 29", "planilha": "EQUIPE 5"},
    "micro30": {"password": "senha30", "role": "micro", "aba": "MICRO 30", "planilha": "EQUIPE 5"},
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
            planilha=user_data["planilha"],
            fechamento=f"FECHAMENTO {user_data['aba']}" if user_data.get("aba") else None
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
                planilha=user_data['planilha'],
                fechamento=f"FECHAMENTO {user_data['aba']}" if user_data.get("aba") else None
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
