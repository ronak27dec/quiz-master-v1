from flask import Blueprint, request, redirect, render_template

from models import db, Subject

subject_controller = Blueprint("subject_controller", __name__)


@subject_controller.route("/create-subject", methods=["GET", "POST"])
def create_subject():
    if request.method == "POST":
        sub_name = request.form["subject_name"]
        sub_description = request.form["subject_description"]
        new_subject = Subject(
            subject_name=sub_name, subject_description=sub_description
        )
        try:
            db.session.add(new_subject)
            db.session.commit()
            return redirect("/admin-dashboard")
        except Exception as e:
            db.session.rollback()
            print(f"Error create subject: {e}")
            return render_template("create_subject.html")
    else:
        return render_template("create_subject.html")


@subject_controller.route("/delete-subject/<int:id>", methods=["GET", "POST"])
def delete_subject(id):
    if request.method == "POST":
        subject = Subject.query.get(id)
        try:
            db.session.delete(subject)
            db.session.commit()
            return redirect("/admin-dashboard")
        except Exception as e:
            db.session.rollback()
            print(f"Error delete subject: {e}")
            return redirect("/admin-dashboard")


@subject_controller.route("/edit-subject/<int:id>", methods=["GET", "POST"])
def edit_subject(id):
    if request.method == "POST":
        subject = Subject.query.get_or_404(id)
        sub_name = request.form["name"]
        sub_description = request.form["subject_description"]
        subject.subject_name = sub_name
        subject.subject_description = sub_description
        try:
            db.session.commit()
            return redirect("/admin-dashboard")
        except Exception as e:
            db.session.rollback()
            print(f"Error edit subject: {e}")
            subject = Subject.query.get_or_404(id)
            return render_template("edit_subject.html", subject=subject)
    else:
        subject = Subject.query.get_or_404(id)
        return render_template("edit_subject.html", subject=subject)
