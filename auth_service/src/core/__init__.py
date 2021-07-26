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
    app.config['SWAGGER'] = {
        'title': 'Auth API',
        'uiversion': 3
    }
    swagger = Swagger(app)

    # Initialize extensions
    db.init_app(app)

    migrate.init_app(app, db)
    ma.init_app(app)
    jwt.init_app(app)

    # Registrate blueprints
    from api.v1.api_bp import bp as api_bp
    app.register_blueprint(api_bp, url_prefix="/api/v1")
    from commands import usersbp
    app.register_blueprint(usersbp)

    from models.user import UserManager
    app.user_manager = UserManager()

    from api.v1.utils import swagger_views

    app.add_url_rule(
        '/api/v1/sign_up',
        view_func=swagger_views.SignUpView.as_view('sign_up'),
        methods=['POST'],

    )
    app.add_url_rule(
        '/api/v1/sign_in',
        view_func=swagger_views.SignInView.as_view('sign_in'),
        methods=['POST']
    )
    app.add_url_rule(
        '/api/v1/sign_out',
        view_func=swagger_views.SignOutView.as_view('sign_out'),
        methods=['POST']
    )
    app.add_url_rule(
        '/api/v1/sign_out_all',
        view_func=swagger_views.SignOutAllView.as_view('sign_out_all'),
        methods=['POST']
    )
    app.add_url_rule(
        '/api/v1/refresh',
        view_func=swagger_views.RefreshView.as_view('refresh'),
        methods=['POST']
    )
    app.add_url_rule(
        '/api/v1/user/update',
        view_func=swagger_views.UpdateView.as_view('update'),
        methods=['PATCH']
    )

    app.add_url_rule(
        '/api/v1/user/history',
        view_func=swagger_views.HistoryView.as_view('history'),
        methods=['GET']
    )
    app.add_url_rule(
        '/api/v1/user/change_password',
        view_func=swagger_views.ChangePasswordView.as_view('change_password'),
        methods=['POST']
    )
    app.add_url_rule(
        '/api/v1/user/me',
        view_func=swagger_views.MeView.as_view('me'),
        methods=['GET']
    )
    app.add_url_rule(
        '/api/v1/user/role',
        view_func=swagger_views.UserRoleView.as_view('role'),
        methods=['GET']
    )
    app.add_url_rule(
        '/api/v1/user/add_role',
        view_func=swagger_views.AddRoleView.as_view('add_role'),
        methods=['POST']
    )
    app.add_url_rule(
        '/api/v1/user/remove_role',
        view_func=swagger_views.RemoveRoleView.as_view('remove_role'),
        methods=['POST']
    )

    app.add_url_rule(
        '/api/v1/roles',
        view_func=swagger_views.RoleView.as_view('get_roles'),
        methods=['GET']
    )
    app.add_url_rule(
        '/api/v1/roles',
        view_func=swagger_views.CreateRoleView.as_view('create_role'),
        methods=['POST']
    )
    app.add_url_rule(
        '/api/v1/roles/<id>',
        view_func=swagger_views.UpdateRoleView.as_view('update_role'),
        methods=['PATCH']
    )
    app.add_url_rule(
        '/api/v1/roles/<id>',
        view_func=swagger_views.DeleteRoleView.as_view('delete_role'),
        methods=['DELETE']
    )

    return app
