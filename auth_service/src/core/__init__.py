from flask import Flask
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flasgger import Swagger
from flask_sqlalchemy import SQLAlchemy

from .config import Config

db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()
jwt = JWTManager()


def create_app(config_class=Config):

    # App configs
    app = Flask(__name__, template_folder="../templates")
    app.config.from_object(config_class)
    swagger = Swagger(app)

    # Initialize extensions
    db.init_app(app)

    migrate.init_app(app, db)
    ma.init_app(app)
    jwt.init_app(app)

    # Registrate blueprints
    from api.v1.api_bp import bp as api_bp
    app.register_blueprint(api_bp, url_prefix="/api/v1")

    from api.v1.utils.swagger_views import SignUpView, SignOutView
    app.add_url_rule(
        '/api/v1/sign_up',
        view_func=SignUpView.as_view('sign_up'),
        methods=['POST']
    )
    app.add_url_rule(
        '/api/v1/sign_out',
        view_func=SignOutView.as_view('sign_out'),
        methods=['POST']
    )

    from commands import usersbp
    app.register_blueprint(usersbp)

    from models.user import UserManager
    app.user_manager = UserManager()

    return app
