from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


# Flask-Login
login_manager = LoginManager()


# Flask-Limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[]
)