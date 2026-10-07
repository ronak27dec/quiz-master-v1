import os
from datetime import datetime

from flask import Flask
from werkzeug.security import generate_password_hash

from controllers.auth_controller import auth_controller
from controllers.chapter_controller import chapter_controller
from controllers.dashboard_controller import dashboard_controller
from controllers.question_controller import question_controller
from controllers.quiz_controller import quiz_controller
from controllers.search_controller import search_controller
from controllers.subject_controller import subject_controller
from controllers.user_controller import user_controller
from models import db, User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quizmaster.db'
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


def create_admin_user():
    full_name = 'Admin'
    email = 'admin@admin.com'
    password = 'admin'
    qualification = 'Masters'
    admin_dob = '1970-01-01'
    dob = datetime.strptime(admin_dob, "%Y-%m-%d")
    hashed_password = generate_password_hash(password)
    user = User.query.filter_by(email=email).first()
    if not user:
        admin_user = User(full_name=full_name,
                          email=email,
                          password=hashed_password,
                          qualification=qualification,
                          dob=dob,
                          is_admin=True)
        try:
            db.session.add(admin_user)
            db.session.commit()
        except Exception as e:
            print(f"Error in creating Admin user: {e}")
            db.session.rollback()


with app.app_context():
    db.create_all()
    create_admin_user()

app.register_blueprint(auth_controller)
app.register_blueprint(dashboard_controller)
app.register_blueprint(subject_controller)
app.register_blueprint(chapter_controller)
app.register_blueprint(quiz_controller)
app.register_blueprint(question_controller)
app.register_blueprint(user_controller)
app.register_blueprint(search_controller)

if __name__ == '__main__':
    app.run(debug=True)
