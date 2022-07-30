from flask import Flask
from flask_jwt_extended import JWTManager
from app.config import Config
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from app.models import UserModel, FilmModel, SessionModel, TicketModel, HallModel, ActorModel, session
from app.cinema import page_not_found


def setup_database(app):
    with app.app_context():
        @app.before_first_request
        def create_tables():
            from app.database.database import db, base
            base.metadata.create_all(db)


def setup_jwt(app):
    jwt = JWTManager(app)

    from app.models import RevokedTokenModel

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blacklist(jwt_header, jwt_payload):
        jti = jwt_payload['jti']
        return RevokedTokenModel.is_jti_blacklisted(jti)


def setup_swagger(app):
    swagger_url = '/swagger'
    api_url = '/static/swagger.yaml'
    swagger_bp = get_swaggerui_blueprint(
        swagger_url,
        api_url,
        config={
            'app_name': "final_proj_cinema"
        }
    )
    app.register_blueprint(swagger_bp, url_prefix=swagger_url)


def setup_admin(app):
    admin = Admin(app, name="MyCinema", template_mode='bootstrap4')
    admin.add_view(ModelView(UserModel, session, name='User'))
    admin.add_view(ModelView(FilmModel, session, name='Film'))
    admin.add_view(ModelView(SessionModel, session, name='Session'))
    admin.add_view(ModelView(TicketModel, session, name='Ticket'))
    admin.add_view(ModelView(HallModel, session, name='Hall'))
    admin.add_view(ModelView(ActorModel, session, name='Actor'))


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['SECRET_KEY'] = 'Sokyrka12031990403'
    app.register_error_handler(404, page_not_found)
    login_manager = LoginManager(app)
    login_manager.login_view = "cinema.login_page"
    login_manager.login_message_category = "info"

    # allow cross-origin resource sharing
    CORS(app)

    @login_manager.user_loader
    def load_user(user_id):
        return session.query(UserModel).get(int(user_id))

    # database first, then blueprints!
    setup_database(app)
    setup_jwt(app)
    setup_admin(app)
    setup_swagger(app)

    from .views import users_bp, auth_bp, films_bp, sessions_bp, halls_bp, tickets_bp, actors_bp
    from .cinema import cinema_bp
    app.register_blueprint(users_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(films_bp)
    app.register_blueprint(sessions_bp)
    app.register_blueprint(halls_bp)
    app.register_blueprint(tickets_bp)
    app.register_blueprint(cinema_bp)
    app.register_blueprint(actors_bp)
    return app
