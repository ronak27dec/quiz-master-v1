import base64
import io

import matplotlib
import matplotlib.pyplot as plt
from flask import Blueprint, request, session, render_template, redirect, flash
from sqlalchemy import func, extract
from werkzeug.security import check_password_hash, generate_password_hash

from models import User, Score, db

user_controller = Blueprint("user_controller", __name__)

matplotlib.use("Agg")


@user_controller.route("/users", methods=["GET", "POST"])
def users():
    if "user_id" not in session:
        return redirect("/")
    else:
        all_user = User.query.filter_by(is_admin=False).all()
        user_id = session["user_id"]
        user = User.query.get(user_id)
        attempts = (
            db.session.query(Score.user_id, func.count(Score.id).label("attempt_count"))
            .group_by(Score.user_id)
            .all()
        )
        total_attempts = {user_id: attempt_count for user_id, attempt_count in attempts}
        if user.is_admin:
            return render_template(
                "users.html",
                user=user,
                all_user=all_user,
                total_attempts=total_attempts,
            )
        else:
            return redirect("/")


@user_controller.route("/user-profile", methods=["GET", "POST"])
def user_profile():
    if "user_id" not in session:
        return redirect("/")
    else:
        user_id = session["user_id"]
        user = User.query.get(user_id)
        scores = (
            Score.query.filter_by(user_id=user_id)
            .order_by(Score.time_stamp_of_attempt.desc())
            .all()
        )
        return render_template("user_profile.html", user=user, scores=scores)


@user_controller.route("/user-details/<int:user_id>", methods=["GET", "POST"])
def user_details(user_id):
    if "user_id" not in session:
        return redirect("/")
    else:
        session_user_id = session["user_id"]
        user = User.query.get(session_user_id)
        scores = (
            Score.query.filter_by(user_id=user_id)
            .order_by(Score.time_stamp_of_attempt.desc())
            .all()
        )
        return render_template("/user_details.html", user=user, scores=scores)


@user_controller.route("/user-delete/<int:user_id>", methods=["GET", "POST"])
def delete_user(user_id):
    if "user_id" is not session:
        return redirect("/")
    else:
        user = User.query.get(user_id)
        if user:
            try:
                db.session.delete(user)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"Error delete user: {e}")
            return redirect("/users")


@user_controller.route("/change-password/<int:user_id>", methods=["GET", "POST"])
def change_password(user_id):
    if request.method == "POST":
        user = User.query.get_or_404(user_id)
        password = user.password
        old_password = request.form["old-password"]
        new_password = request.form["new-password"]
        re_enter_password = request.form["reenter-password"]
        if (
            check_password_hash(user.password, old_password)
            and new_password == re_enter_password
        ):
            user.password = generate_password_hash(new_password)
            try:
                db.session.commit()
                flash("Password updated successfully")
                return redirect("/user-profile")
            except Exception as e:
                db.session.rollback()
                flash("Something went wrong")
                print(f"Error change password: {e}")
                return render_template("change_password.html", user=user)
        else:
            user_id = session["user_id"]
            user = User.query.get(user_id)
            flash(
                "Unable to update password. Please check your password and retry again."
            )
            return render_template("change_password.html", user=user)
    else:
        user_id = session["user_id"]
        user = User.query.get(user_id)
        return render_template("change_password.html", user=user)


@user_controller.route("/user-summary/<int:user_id>", methods=["GET", "POST"])
def user_summary(user_id):
    userID = session["user_id"]
    user = User.query.get(userID)

    img_base64 = plot_number_of_quiz_per_sub(user_id=user_id)
    img_base64_monthly = plot_number_of_quiz_per_month(user_id=user_id)
    img_scatter = scatter_plot(user_id=user_id)
    return render_template(
        "user_summary.html",
        user=user,
        img_base64=img_base64,
        img_base64_monthly=img_base64_monthly,
        img_scatter=img_scatter,
    )


@user_controller.route("/user-statistics", methods=["GET", "POST"])
def user_statistics():
    user_id = session["user_id"]
    user = User.query.get(user_id)

    img_base64 = stat_plot_number_of_quiz_per_sub()
    img_base64_monthly = stat_plot_number_of_quiz_per_month()
    img_scatter = stat_scatter_plot()
    img_highest_marks = stat_plot_highest_marks_per_sub()
    return render_template(
        "user_statistics.html",
        user=user,
        img_base64=img_base64,
        img_base64_monthly=img_base64_monthly,
        img_scatter=img_scatter,
        img_highest_marks=img_highest_marks,
    )


@user_controller.route("/user-flag/<int:user_id>", methods=["GET", "POST"])
def flag_user(user_id):
    if request.method == "POST":
        user = User.query.get(user_id)
        if user.is_flagged:
            user.is_flagged = False
        else:
            user.is_flagged = True
        try:
            db.session.commit()
            return redirect("/users")
        except Exception as e:
            print(f"Error flag user: {e}")
            redirect("/")


def stat_plot_highest_marks_per_sub():
    highest_scores = get_highest_scores_per_subject()

    subjects = [row[0] for row in highest_scores]
    scores = [row[1] for row in highest_scores]

    plt.figure(figsize=(10, 6))
    plt.bar(subjects, scores, color="royalblue")
    plt.xlabel("Subjects")
    plt.ylabel("Highest Scores")
    plt.title("Highest Scores per Subject")
    plt.xticks(rotation=0, ha="right")
    plt.tight_layout()

    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    plt.close()

    img_base64 = base64.b64encode(img.getvalue()).decode("utf-8")
    return img_base64


def plot_number_of_quiz_per_sub(user_id):
    subject_quiz_counts = get_subject_quiz_counts(user_id=user_id)

    subjects = [row[0] for row in subject_quiz_counts]
    quiz_counts = [row[1] for row in subject_quiz_counts]

    plt.figure(figsize=(10, 6))
    plt.bar(subjects, quiz_counts, color="royalblue")
    plt.xlabel("Subjects")
    plt.ylabel("Number of Quizzes")
    plt.title("Number of Quizzes per subject")
    plt.xticks(rotation=0, ha="right")
    plt.tight_layout()

    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    plt.close()
    get_quizzes_per_month(user_id=user_id)
    img_base64 = base64.b64encode(img.getvalue()).decode("utf-8")
    return img_base64


def stat_plot_number_of_quiz_per_sub():
    subject_quiz_counts = stat_get_subject_quiz_counts()

    subjects = [row[0] for row in subject_quiz_counts]
    quiz_counts = [row[1] for row in subject_quiz_counts]

    plt.figure(figsize=(10, 6))
    plt.bar(subjects, quiz_counts, color="royalblue")
    plt.xlabel("Subjects")
    plt.ylabel("Number of Quizzes")
    plt.title("Number of Quizzes per subject")
    plt.xticks(rotation=0, ha="right")
    plt.tight_layout()

    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    plt.close()
    stat_get_quizzes_per_month()
    img_base64 = base64.b64encode(img.getvalue()).decode("utf-8")
    return img_base64


def plot_number_of_quiz_per_month(user_id):
    quizzes_per_month = get_quizzes_per_month(user_id=user_id)
    months = [row[0] for row in quizzes_per_month]
    quiz_counts = [row[1] for row in quizzes_per_month]

    plt.figure(figsize=(10, 6))
    plt.bar(months, quiz_counts, color="royalblue")
    plt.xlabel("Month")
    plt.ylabel("Number of Quizzes Attempted")
    plt.title("Quizzes Attempted per Month")
    plt.xticks(rotation=0, ha="right")
    plt.tight_layout()

    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    plt.close()

    img_base64 = base64.b64encode(img.getvalue()).decode("utf-8")
    return img_base64


def stat_plot_number_of_quiz_per_month():
    quizzes_per_month = stat_get_quizzes_per_month()

    months = [row[0] for row in quizzes_per_month]
    quiz_counts = [row[1] for row in quizzes_per_month]

    plt.figure(figsize=(10, 6))
    plt.bar(months, quiz_counts, color="royalblue")
    plt.xlabel("Month")
    plt.ylabel("Number of Quizzes Attempted")
    plt.title("Quizzes Attempted per Month")
    plt.xticks(rotation=0, ha="right")
    plt.tight_layout()

    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    plt.close()

    img_base64 = base64.b64encode(img.getvalue()).decode("utf-8")
    return img_base64


def get_subject_quiz_counts(user_id):
    subject_quiz_counts = (
        db.session.query(
            Score.subject_name, func.count(Score.quiz_id).label("quiz_count")
        )
        .filter(Score.user_id == user_id)
        .group_by(Score.subject_name)
        .all()
    )
    return subject_quiz_counts


def stat_get_subject_quiz_counts():
    subject_quiz_counts = (
        db.session.query(
            Score.subject_name, func.count(Score.quiz_id).label("quiz_count")
        )
        .group_by(Score.subject_name)
        .all()
    )
    return subject_quiz_counts


def get_quizzes_per_month(user_id):
    quizzes_per_month = (
        db.session.query(
            extract("year", Score.time_stamp_of_attempt).label("year"),
            extract("month", Score.time_stamp_of_attempt).label("month"),
            func.count(Score.quiz_id).label("quiz_count"),
        )
        .filter(Score.user_id == user_id)
        .group_by("year", "month")
        .order_by("year", "month")
        .all()
    )

    formatted_data = [
        (f"{int(row[0])}-{int(row[1]):02d}", row[2]) for row in quizzes_per_month
    ]
    return formatted_data


def stat_get_quizzes_per_month():
    quizzes_per_month = (
        db.session.query(
            extract("year", Score.time_stamp_of_attempt).label("year"),
            extract("month", Score.time_stamp_of_attempt).label("month"),
            func.count(Score.quiz_id).label("quiz_count"),
        )
        .group_by("year", "month")
        .order_by("year", "month")
        .all()
    )

    formatted_data = [
        (f"{int(row[0])}-{int(row[1]):02d}", row[2]) for row in quizzes_per_month
    ]
    return formatted_data


def get_score_data(user_id):
    score_data = (
        db.session.query(
            Score.total_scored,
            Score.percentage_score,
            Score.total_correct_answer,
            Score.total_questions,
            Score.time_stamp_of_attempt,
        )
        .filter(Score.user_id == user_id)
        .all()
    )
    return score_data


def stat_get_score_data():
    score_data = db.session.query(
        Score.total_scored,
        Score.percentage_score,
        Score.total_correct_answer,
        Score.total_questions,
        Score.time_stamp_of_attempt,
    ).all()
    return score_data


def scatter_plot(user_id):
    score_data = get_score_data(user_id=user_id)

    total_scored = [row[0] for row in score_data]
    percentage_scores = [row[1] for row in score_data]

    plt.figure(figsize=(10, 6))
    plt.scatter(total_scored, percentage_scores, color="royalblue")
    plt.xlabel("Total Scored")
    plt.ylabel("Percentage Score")
    plt.title("Total Scored vs Percentage Score")
    plt.grid(True)
    plt.tight_layout()

    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    plt.close()

    img_base64 = base64.b64encode(img.getvalue()).decode("utf-8")
    return img_base64


def stat_scatter_plot():
    score_data = stat_get_score_data()

    total_scored = [row[0] for row in score_data]
    percentage_scores = [row[1] for row in score_data]

    plt.figure(figsize=(10, 6))
    plt.scatter(total_scored, percentage_scores, color="royalblue")
    plt.xlabel("Total Scored")
    plt.ylabel("Percentage Score")
    plt.title("Total Scored vs Percentage Score")
    plt.grid(True)
    plt.tight_layout()

    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    plt.close()

    img_base64 = base64.b64encode(img.getvalue()).decode("utf-8")
    return img_base64


def get_highest_scores_per_subject():
    highest_scores = (
        db.session.query(
            Score.subject_name, func.max(Score.total_scored).label("highest_score")
        )
        .group_by(Score.subject_name)
        .all()
    )
    return highest_scores
