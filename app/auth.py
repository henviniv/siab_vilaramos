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



@login_manager.user_loader
def load_user(user_id):
    try:
        resposta = (
            supabase
            .table("usuarios")
            .select("username, role, micro, equipe")
            .eq("username", user_id)
            .execute()
        )

        if not resposta.data:
            return None

        user_data = resposta.data[0]

        return User(
            id=user_data["username"],
            username=user_data["username"],
            role=user_data["role"],
            micro=user_data.get("micro"),
            equipe=user_data.get("equipe")
        )

    except Exception as e:
        print(f"Erro ao carregar usuário: {e}")
        return None

@auth_bp.route('/login', methods=['GET','POST'])
def login():

    if request.method == "POST":

        username = request.form["username"].strip()
        senha = request.form["password"]

        resposta = (
            supabase
            .table("usuarios")
            .select("*")
            .eq("username", username)
            .execute()
        )

        if resposta.data:
            user_data = resposta.data[0]

            if check_password_hash(user_data["password_hash"], senha):

                user = User(
                    id=user_data["username"],
                    username=user_data["username"],
                    role=user_data["role"],
                    micro=user_data.get("micro"),
                    equipe=user_data.get("equipe")
                )

                login_user(user)

                print("[LOGIN]", user.username, "MICRO:", user.micro, "EQUIPE:", user.equipe)

                return redirect(url_for("main.index"))

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
