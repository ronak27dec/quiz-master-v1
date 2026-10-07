from flask import Blueprint, request, redirect, render_template, session, flash

from models import db, Quiz, User, Question

question_controller = Blueprint('question_controller', __name__)


@question_controller.route('/question/<quiz_id>')
def question(quiz_id):
    if 'user_id' not in session:
        return redirect('/')
    else:
        user_id = session['user_id']
        user = User.query.get(user_id)
        quiz = Quiz.query.get_or_404(quiz_id)
        return render_template('question.html', quiz=quiz, user=user)


@question_controller.route('/create-question/<quiz_id>', methods=['GET', 'POST'])
def create_question(quiz_id):
    if request.method == 'POST':
        question_title = request.form["title"]
        option_a = request.form["option-a"]
        option_b = request.form["option-b"]
        option_c = request.form["option-c"]
        option_d = request.form["option-d"]
        correct_option = request.form["correct-option"]

        if correct_option not in [option_a, option_b, option_c, option_d]:
            flash('Correct option must be one of the provided options.')
            return redirect('/create-question/' + str(quiz_id))
        else:
            new_question = Question(question_title=question_title,
                                    option_a=option_a,
                                    option_b=option_b,
                                    option_c=option_c,
                                    option_d=option_d,
                                    correct_option=correct_option,
                                    quiz_id=quiz_id,
                                    )
            try:
                db.session.add(new_question)
                db.session.commit()
                return redirect('/question/' + str(quiz_id))
            except Exception as e:
                db.session.rollback()
                print(f"Error create question: {e}")
                quiz = Quiz.query.get_or_404(quiz_id)
                return render_template('create_question.html', quiz=quiz)
    else:
        quiz = Quiz.query.get_or_404(quiz_id)
        return render_template('create_question.html', quiz=quiz)


@question_controller.route('/edit-question/<int:question_id>', methods=['GET', 'POST'])
def edit_question(question_id):
    if request.method == 'POST':
        question = Question.query.get_or_404(question_id)
        quiz_id = question.quiz_id
        question_title = request.form["title"]
        option_a = request.form["option-a"]
        option_b = request.form["option-b"]
        option_c = request.form["option-c"]
        option_d = request.form["option-d"]
        correct_option = request.form["correct-option"]
        question.question_title = question_title
        question.option_a = option_a
        question.option_b = option_b
        question.option_c = option_c
        question.option_d = option_d
        question.correct_option = correct_option
        question.quiz_id = quiz_id
        try:
            db.session.commit()
            return redirect('/question/' + str(quiz_id))
        except Exception as e:
            db.session.rollback()
            print(f"Error edit question: {e}")
            question = Question.query.get_or_404(question_id)
            return render_template('edit_question.html', question=question)
    else:
        question = Question.query.get_or_404(question_id)
        return render_template('edit_question.html', question=question)


@question_controller.route('/delete-question/<int:question_id>', methods=['GET', 'POST'])
def delete_question(question_id):
    if request.method == 'POST':
        question = Question.query.get_or_404(question_id)
        quiz_id = question.quiz_id
        try:
            db.session.delete(question)
            db.session.commit()
            return redirect('/question/' + str(quiz_id))
        except Exception as e:
            db.session.rollback()
            print(f"Error delete question: {e}")
            return redirect('/question/' + str(quiz_id))


@question_controller.route('/user-question/<int:quiz_id>', methods=['GET', 'POST'])
def user_question(quiz_id):
    if 'user_id' not in session:
        return redirect('/')
    else:
        user_id = session['user_id']
        user = User.query.get(user_id)
        quiz = Quiz.query.get_or_404(quiz_id)
        return render_template('/user_question.html', user=user, quiz=quiz)
