from flask import Blueprint, session, redirect, render_template

from models import User, Subject

dashboard_controller = Blueprint('dashboard_controller', __name__)


@dashboard_controller.route("/admin-dashboard", methods=['GET', 'POST'])
def admin_dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    else:
        user_id = session['user_id']
        user = User.query.get(user_id)
        subjects = Subject.query.order_by(Subject.subject_name.asc()).all()
        return render_template('admin_dashboard.html', subjects=subjects, user=user)


@dashboard_controller.route("/user-dashboard", methods=['GET', 'POST'])
def user_dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    else:
        user_id = session['user_id']
        user = User.query.get(user_id)
        subjects = Subject.query.order_by(Subject.subject_name.asc()).all()
        return render_template('/user_dashboard.html', subjects=subjects, user=user)
