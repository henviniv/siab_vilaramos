from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import check_password_hash
from app.supabase_db import supabase

auth_bp = Blueprint('auth', __name__)
login_manager = LoginManager()

# Classe de usuário para o Flask-Login
class User(UserMixin):
    def __init__(self, id, username, role, micro=None, equipe=None):
        self.id = id
        self.username = username
        self.role = role
        self.micro = micro
        self.equipe = equipe

# Dicionário de usuários
USERS = {
    "admin": {
        "password": "ramos2025",
        "role": "admin",
        "micro": None,
        "equipe": None
    },
    "micro01": {"password": "eli1611", "role": "micro", "micro": "MI 01", "equipe": "EQUIPE 1"},
    "micro02": {"password": "585283vb", "role": "micro", "micro": "MI 02", "equipe": "EQUIPE 1"},
    "micro03": {"password": "miewag7681", "role": "micro", "micro": "MI 03", "equipe": "EQUIPE 1"},
    "micro04": {"password": "920795g", "role": "micro", "micro": "MI 04", "equipe": "EQUIPE 1"},
    "micro05": {"password": "134579", "role": "micro", "micro": "MI 05", "equipe": "EQUIPE 1"},
    "micro06": {"password": "gigu0106", "role": "micro", "micro": "MI 06", "equipe": "EQUIPE 1"},
    "micro07": {"password": "223344ma", "role": "micro", "micro": "MICRO 7", "equipe": "EQUIPE 2"},
    "micro08": {"password": "r4828", "role": "micro", "micro": "MICRO 8", "equipe": "EQUIPE 2"},
    "micro09": {"password": "Samuel2025", "role": "micro", "micro": "MICRO 9", "equipe": "EQUIPE 2"},
    "micro10": {"password": "manuella3004", "role": "micro", "micro": "MICRO 10", "equipe": "EQUIPE 2"},
    "micro11": {"password": "Mar617318", "role": "micro", "micro": "MICRO 11", "equipe": "EQUIPE 2"},
    "micro12": {"password": "a95792315", "role": "micro", "micro": "MICRO 12", "equipe": "EQUIPE 2"},
    "micro13": {"password": "balada10", "role": "micro", "micro": "MICRO 13", "equipe": "EQUIPE 3"},
    "micro14": {"password": "96063404m", "role": "micro", "micro": "MICRO 14", "equipe": "EQUIPE 3"},
    "micro15": {"password": "4303li", "role": "micro", "micro": "MICRO 15", "equipe": "EQUIPE 3"},
    "micro16": {"password": "RE00316#", "role": "micro", "micro": "MICRO 16", "equipe": "EQUIPE 3"},
    "micro17": {"password": "de123", "role": "micro", "micro": "MICRO 17", "equipe": "EQUIPE 3"},
    "micro18": {"password": "@vr12345", "role": "micro", "micro": "MICRO 18", "equipe": "EQUIPE 3"},
    "micro19": {"password": "Monic@123", "role": "micro", "micro": "MICRO 19", "equipe": "EQUIPE 4"},
    "micro20": {"password": "senha20", "role": "micro", "micro": "MICRO 20", "equipe": "EQUIPE 4"},
    "micro21": {"password": "Na130689", "role": "micro", "micro": "MICRO 21", "equipe": "EQUIPE 4"},
    "micro22": {"password": "senha22", "role": "micro", "micro": "MICRO 22", "equipe": "EQUIPE 4"},
    "micro23": {"password": "Hidek_22", "role": "micro", "micro": "MICRO 23", "equipe": "EQUIPE 4"},
    "micro24": {"password": "30242202Ra", "role": "micro", "micro": "MICRO 24", "equipe": "EQUIPE 4"},
    "micro25": {"password": "419905", "role": "micro", "micro": "MICRO 25", "equipe": "EQUIPE 5"},
    "micro26": {"password": "123preto", "role": "micro", "micro": "MICRO 26", "equipe": "EQUIPE 5"},
    "micro27": {"password": "Gis512629", "role": "micro", "micro": "MICRO 27", "equipe": "EQUIPE 5"},
    "micro28": {"password": "Luna@2030", "role": "micro", "micro": "MICRO 28", "equipe": "EQUIPE 5"},
    "micro29": {"password": "NAnu4483", "role": "micro", "micro": "MICRO 29", "equipe": "EQUIPE 5"},
    "micro30": {"password": "110893He", "role": "micro", "micro": "MICRO 30", "equipe": "EQUIPE 5"},
}

@login_manager.user_loader
def load_user(user_id):

    user_data = USERS.get(user_id)

    if user_data:

        return User(
            id=user_id,
            username=user_id,
            role=user_data["role"],
            micro=user_data.get("micro"),
            equipe=user_data.get("equipe")
        )

    return None

@auth_bp.route('/login', methods=['GET','POST'])
def login():

    if request.method == "POST":

        username = request.form['username']
        senha = request.form['password']

        user_data = USERS.get(username)


        if user_data and senha == user_data["password"]:

            user = User(
                id=username,
                username=username,
                role=user_data["role"],
                micro=user_data.get("micro"),
                equipe=user_data.get("equipe")
            )

            login_user(user)

            print("[LOGIN]", user.username, "MICRO:", user.micro, "EQUIPE:", user.equipe)

            return redirect(
                url_for("main.index")
            )


        flash(
            "Usuário ou senha inválidos",
            "danger"
        )

    return render_template("login.html")

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))
