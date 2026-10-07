from datetime import datetime

from flask import Blueprint, request, session, redirect, render_template, flash
from werkzeug.security import check_password_hash, generate_password_hash

from models import User, db

auth_controller = Blueprint('auth_controller', __name__)


@auth_controller.route('/')
def home():
    return redirect('/login')

# this is a comment
@auth_controller.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password) and not user.is_flagged:
            session["user_id"] = user.id
            if user.is_admin:
                return redirect('admin-dashboard')
            else:
                return redirect('user-dashboard')
        else:
            flash("Login failed. Check your username and/or password.", "danger")
            return render_template('login.html')
    else:
        return render_template('login.html')


@auth_controller.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        full_name = request.form['full_name']
        password = request.form['password']
        email = request.form['email']
        qualification = request.form['qualification']
        user_dob = request.form['dob']
        dob = datetime.strptime(user_dob, "%Y-%m-%d").date()
        existing_user = User.query.filter_by(email=email).first()
        hashed_password = generate_password_hash(password)
        if existing_user:
            flash("Error: A user with this email already exists!", "error")
            return redirect('/register')
        else:
            new_user = User(full_name=full_name,
                            password=hashed_password,
                            email=email,
                            qualification=qualification,
                            dob=dob,
                            is_admin=False)
            try:
                db.session.add(new_user)
                db.session.commit()
                return redirect('/login')
            except Exception as e:
                db.session.rollback()
                print(f"Registration Error: {e}")
                return redirect('/register')
    else:
        return render_template('register.html')


@auth_controller.route('/logout', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        session.clear()
        return redirect('/login')
