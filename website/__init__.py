from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from os import path
from werkzeug.security import generate_password_hash
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secretkey'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Discussion, Message

    with app.app_context():
        db.create_all()

        # Create a default admin
        admin_user = User.query.filter_by(username='Admin', role='admin').first()
        if not admin_user:
            admin_user = User(role='admin', username='Admin', email='admin@email.com', password=generate_password_hash('Aa1234!@#$'), profile_picture='default.jpg')
            db.session.add(admin_user)
            db.session.commit()

        # Create a default discussion by the admin if not exists
        default_discussion = Discussion.query.filter_by(title='Welcome to AnimeExplorer', user_id=admin_user.id).first()
        if not default_discussion:
            default_discussion = Discussion(title='Welcome to AnimeExplorer', user_id=admin_user.id)
            db.session.add(default_discussion)
            db.session.commit()

        # Create a default message in the default discussion if not exists
        default_message = Message.query.filter_by(discussion_id=default_discussion.id).first()
        if not default_message:
            default_message = Message(text='Thank you for using AnimeExplorer. If you have questions related to this website, feel free to ask below!', user_id=admin_user.id, discussion_id=default_discussion.id)
            db.session.add(default_message)
            db.session.commit()
        


    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @app.template_filter('jinja_max')
    def jinja_max(value, arg):
        return max(value, arg)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    @app.errorhandler(400)
    def bad_request_error(error):
        return render_template('errors/400.html'), 400
    
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        return render_template('errors/500.html'), 500

    @app.errorhandler(503)
    def service_unavilable_error(error):
        return render_template('errors/503.html'), 503

    @app.route('/error/400')
    def trigger_400_error():
        return bad_request_error(400)

    @app.route('/error/403')
    def trigger_403_error():
        return forbidden_error(403)

    @app.route('/error/404')
    def trigger_404_error():
        return not_found_error(404)

    @app.route('/error/500')
    def trigger_500_error():
        return internal_server_error(500)

    @app.route('/error/503')
    def trigger_503_error():
        return service_unavilable_error(503)

    return app
