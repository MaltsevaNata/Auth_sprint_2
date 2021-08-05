from flasgger import Swagger
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_opentracing import FlaskTracer
from flask_sqlalchemy import SQLAlchemy

from .config import Config

URL_PREFIX = "/auth/v1"

db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()
jwt = JWTManager()
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])


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
    limiter.init_app(app)

    import core.jaeger as jaeger
    jaeger.tracer = FlaskTracer(jaeger._setup_jaeger, app=app)

    # Registrate blueprints
    from api.v1.api_bp import bp as api_bp
    app.register_blueprint(api_bp, url_prefix=URL_PREFIX)
    from commands import usersbp
    app.register_blueprint(usersbp)

    from models.user import UserManager
    app.user_manager = UserManager()
    from models.google_user import GoogleUserManager
    app.google_user_manager = GoogleUserManager()
    from .SocialAuthorizer import GoogleAuthorizer
    app.google_authorizer = GoogleAuthorizer()

    from api.v1.utils import swagger_views

    app.add_url_rule(
        URL_PREFIX + '/sign_up',
        view_func=swagger_views.SignUpView.as_view('sign_up'),
        methods=['POST'],

    )
    app.add_url_rule(
        URL_PREFIX + '/sign_in',
        view_func=swagger_views.SignInView.as_view('sign_in'),
        methods=['POST']
    )
    app.add_url_rule(
        URL_PREFIX + '/sign_out',
        view_func=swagger_views.SignOutView.as_view('sign_out'),
        methods=['POST']
    )
    app.add_url_rule(
        URL_PREFIX + '/sign_out_all',
        view_func=swagger_views.SignOutAllView.as_view('sign_out_all'),
        methods=['POST']
    )
    app.add_url_rule(
        URL_PREFIX + '/refresh',
        view_func=swagger_views.RefreshView.as_view('refresh'),
        methods=['POST']
    )
    app.add_url_rule(
        URL_PREFIX + '/update',
        view_func=swagger_views.UpdateView.as_view('update'),
        methods=['PATCH']
    )

    app.add_url_rule(
        URL_PREFIX + '/user/history',
        view_func=swagger_views.HistoryView.as_view('history'),
        methods=['GET']
    )
    app.add_url_rule(
        URL_PREFIX + '/user/change_password',
        view_func=swagger_views.ChangePasswordView.as_view('change_password'),
        methods=['POST']
    )
    app.add_url_rule(
        URL_PREFIX + '/user/me',
        view_func=swagger_views.MeView.as_view('me'),
        methods=['GET']
    )
    app.add_url_rule(
        URL_PREFIX + '/user/role',
        view_func=swagger_views.UserRoleView.as_view('role'),
        methods=['GET']
    )
    app.add_url_rule(
        URL_PREFIX + '/user/add_role',
        view_func=swagger_views.AddRoleView.as_view('add_role'),
        methods=['POST']
    )
    app.add_url_rule(
        URL_PREFIX + '/user/remove_role',
        view_func=swagger_views.RemoveRoleView.as_view('remove_role'),
        methods=['POST']
    )

    app.add_url_rule(
        URL_PREFIX + '/roles',
        view_func=swagger_views.RoleView.as_view('get_roles'),
        methods=['GET']
    )
    app.add_url_rule(
        URL_PREFIX + '/roles',
        view_func=swagger_views.CreateRoleView.as_view('create_role'),
        methods=['POST']
    )
    app.add_url_rule(
        URL_PREFIX + '/roles/<id>',
        view_func=swagger_views.UpdateRoleView.as_view('update_role'),
        methods=['PATCH']
    )
    app.add_url_rule(
        URL_PREFIX + '/roles/<id>',
        view_func=swagger_views.DeleteRoleView.as_view('delete_role'),
        methods=['DELETE']
    )

    return app
