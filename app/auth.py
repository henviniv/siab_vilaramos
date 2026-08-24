from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    request,
    flash
)

from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user,
    UserMixin
)

from werkzeug.security import check_password_hash

from app.supabase_db import supabase
from app.extensions import login_manager, limiter


auth_bp = Blueprint("auth", __name__)


# ============================================================
# USUÁRIO
# ============================================================

class User(UserMixin):

    def __init__(
        self,
        id,
        username,
        role,
        micro=None,
        equipe=None
    ):
        self.id = id
        self.username = username
        self.role = role
        self.micro = micro
        self.equipe = equipe


# ============================================================
# USER LOADER
# ============================================================

@login_manager.user_loader
def load_user(user_id):

    try:

        resposta = (
            supabase
            .table("usuarios")
            .select(
                "username, role, micro, equipe"
            )
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

        print(
            f"[ERRO USER LOADER] {e}"
        )

        return None


# ============================================================
# LOGIN
# ============================================================

@auth_bp.route(
    "/login",
    methods=["GET", "POST"]
)
@limiter.limit(
    "5 per minute",
    methods=["POST"]
)
def login():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        senha = request.form.get(
            "password",
            ""
        )

        # ----------------------------------------------------
        # VALIDAÇÃO
        # ----------------------------------------------------

        if not username or not senha:

            flash(
                "Usuário ou senha inválidos",
                "danger"
            )

            return redirect(
                url_for("auth.login")
            )

        # ----------------------------------------------------
        # BUSCA USUÁRIO
        # ----------------------------------------------------

        try:

            resposta = (
                supabase
                .table("usuarios")
                .select(
                    "username, password_hash, role, micro, equipe"
                )
                .eq("username", username)
                .execute()
            )

        except Exception as e:

            print(
                f"[ERRO LOGIN SUPABASE] {e}"
            )

            flash(
                "Não foi possível realizar o login. Tente novamente.",
                "danger"
            )

            return redirect(
                url_for("auth.login")
            )

        # ----------------------------------------------------
        # VERIFICA SENHA
        # ----------------------------------------------------

        if resposta.data:

            user_data = resposta.data[0]

            try:

                senha_correta = check_password_hash(
                    user_data["password_hash"],
                    senha
                )

            except Exception as e:

                print(
                    f"[ERRO PASSWORD HASH] {e}"
                )

                senha_correta = False

            if senha_correta:

                user = User(
                    id=user_data["username"],
                    username=user_data["username"],
                    role=user_data["role"],
                    micro=user_data.get("micro"),
                    equipe=user_data.get("equipe")
                )

                login_user(user)

                print(
                    "[LOGIN]",
                    user.username,
                    "MICRO:",
                    user.micro,
                    "EQUIPE:",
                    user.equipe
                )

                return redirect(
                    url_for("main.index")
                )

        # ----------------------------------------------------
        # LOGIN INVÁLIDO
        # ----------------------------------------------------

        flash(
            "Usuário ou senha inválidos",
            "danger"
        )

        return redirect(
            url_for("auth.login")
        )

    return render_template(
        "login.html"
    )


# ============================================================
# LOGOUT
# ============================================================

@auth_bp.route("/logout")
@login_required
def logout():

    print(
        "[LOGOUT]",
        current_user.username
    )

    logout_user()

    return redirect(
        url_for("auth.login")
    )