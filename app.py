from flask import Flask, redirect, session
from extensions import db, migrate
from models import Department
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.superadmin import superadmin_bp
from routes.employee import employee_bp
from routes.ad import ad_bp
from routes.lab_incharge import lab_incharge_bp
from signup_route import signup_bp

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'rshandilya'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stationary.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(auth_bp)
    app.register_blueprint(signup_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(superadmin_bp)
    app.register_blueprint(employee_bp)
    app.register_blueprint(ad_bp)
    app.register_blueprint(lab_incharge_bp)

    @app.route('/')
    def home():
        return redirect('/login')

    @app.context_processor
    def inject_is_ad_or_head():
            user_id = session.get('user_id')
            is_ad_or_head = False
            if user_id:
                is_ad_or_head = Department.query.filter(
                    (Department.head_id == user_id) | (Department.ad_id == user_id)
                ).first() is not None
            return dict(is_ad_or_head=is_ad_or_head)

    
    return app
app = create_app()
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)