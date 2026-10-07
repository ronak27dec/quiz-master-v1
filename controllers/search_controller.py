from flask import Blueprint, request, render_template, session, redirect

from models import User, Subject, Chapter, Quiz, Question

search_controller = Blueprint("search_controller", __name__)


@search_controller.route("/search", methods=["GET", "POST"])
def search():
    if "user_id" not in session:
        return redirect("/")

    query = request.args.get("query", "")
    user_id = session["user_id"]
    user = User.query.get(user_id)

    if query:
        users = User.query.filter(
            (User.full_name.ilike(f"%{query}%"))
            | (User.email.ilike(f"%{query}%"))
            | (User.qualification.ilike(f"%{query}%"))
        ).all()

        subjects = Subject.query.filter(
            (Subject.subject_name.ilike(f"%{query}%"))
            | (Subject.subject_description.ilike(f"%{query}%"))
        ).all()

        chapters = Chapter.query.filter(
            (Chapter.chapter_name.ilike(f"%{query}%"))
            | (Chapter.chapter_description.ilike(f"%{query}%"))
        ).all()

        quizzes = Quiz.query.filter((Quiz.quiz_name.ilike(f"%{query}%"))).all()

        questions = Question.query.filter(
            (Question.question_title.ilike(f"%{query}%"))
            | (Question.option_a.ilike(f"%{query}%"))
            | (Question.option_b.ilike(f"%{query}%"))
            | (Question.option_c.ilike(f"%{query}%"))
            | (Question.option_d.ilike(f"%{query}%"))
        ).all()

        return render_template(
            "search_result.html",
            query=query,
            users=users,
            subjects=subjects,
            chapters=chapters,
            quizzes=quizzes,
            questions=questions,
            user=user,
        )

    return render_template("search_result.html", query=None, user=user)
