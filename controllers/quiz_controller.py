from datetime import datetime

from flask import Blueprint, request, redirect, render_template, session, flash

from models import db, Chapter, Quiz, User, Score, Subject, Question

quiz_controller = Blueprint('quiz_controller', __name__)


@quiz_controller.route('/quiz/<int:chapter_id>')
def quiz(chapter_id):
    if 'user_id' not in session:
        return redirect('/')
    else:
        user_id = session['user_id']
        user = User.query.get(user_id)
        chapter = Chapter.query.get_or_404(chapter_id)
        quizzes = Quiz.query.filter_by(chapter_id=chapter_id).order_by(Quiz.quiz_date.asc()).all()
        quiz_data = []
        for quiz in quizzes:
            num_questions = len(quiz.questions)
            quiz_data.append({
                'quiz': quiz,
                'num_questions': num_questions
            })
        return render_template('quiz.html',
                               quizzes=quizzes,
                               chapter=chapter,
                               user=user,
                               current_date=datetime.now().date(),
                               quiz_data=quiz_data)


@quiz_controller.route('/create-quiz/<chapter_id>', methods=['GET', 'POST'])
def create_quiz(chapter_id):
    if request.method == 'POST':
        quiz_name = request.form['name']
        quiz_duration = request.form['duration']
        quiz_date_str = request.form['date'].strip()
        quiz_date = datetime.strptime(quiz_date_str, "%Y-%m-%d")
        quiz_remark = request.form['remark']

        if quiz_date.date() < datetime.now().date():
            flash('The quiz date cannot be in the past. Please select a future date.')
            chapter = Chapter.query.get_or_404(chapter_id)
            return render_template('create_quiz.html', chapter=chapter)
        else:
            new_quiz = Quiz(quiz_name=quiz_name,
                            quiz_duration=quiz_duration,
                            quiz_date=quiz_date,
                            quiz_remark=quiz_remark,
                            chapter_id=chapter_id)
            try:
                db.session.add(new_quiz)
                db.session.commit()
                return redirect('/quiz/' + str(chapter_id))
            except Exception as e:
                db.session.rollback()
                print(f"Error create quiz: {e}")
                chapter = Chapter.query.get_or_404(chapter_id)
                return render_template('create_quiz.html', chapter=chapter)
    else:
        chapter = Chapter.query.get_or_404(chapter_id)
        return render_template('create_quiz.html', chapter=chapter)


@quiz_controller.route('/edit-quiz/<int:quiz_id>', methods=['GET', 'POST'])
def edit_quiz(quiz_id):
    if request.method == 'POST':
        quiz = Quiz.query.get_or_404(quiz_id)
        chapter_id = quiz.chapter_id
        quiz.quiz_name = request.form['name']
        quiz_date_str = request.form['date']
        quiz_date = datetime.strptime(quiz_date_str, "%Y-%m-%d")
        quiz.quiz_date = quiz_date
        quiz.quiz_duration = request.form['duration']
        quiz.quiz_remark = request.form['remark']
        quiz.chapter_id = chapter_id
        try:
            db.session.commit()
            return redirect('/quiz/' + str(chapter_id))
        except Exception as e:
            db.session.rollback()
            print(f"Error edit quiz: {e}")
            quiz = Quiz.query.get_or_404(quiz_id)
            return render_template('edit_quiz.html', quiz=quiz)
    else:
        quiz = Quiz.query.get_or_404(quiz_id)
        return render_template('edit_quiz.html', quiz=quiz)


@quiz_controller.route('/delete-quiz/<int:quiz_id>', methods=['GET', 'POST'])
def delete_quiz(quiz_id):
    if request.method == 'POST':
        quiz = Quiz.query.get(quiz_id)
        chapter_id = quiz.chapter_id
        try:
            db.session.delete(quiz)
            db.session.commit()
            return redirect('/quiz/' + str(chapter_id))
        except Exception as e:
            db.session.rollback()
            print(f"Error delete quiz: {e}")
            return redirect('/quiz/' + str(chapter_id))


@quiz_controller.route('/submit-quiz/<int:quiz_id>', methods=['GET', 'POST'])
def submit_quiz(quiz_id):
    if request.method == 'POST':
        user_id = session['user_id']
        user = User.query.get(user_id)
        quiz = Quiz.query.get_or_404(quiz_id)
        chapter = Chapter.query.get_or_404(quiz.chapter_id)
        subject = Subject.query.get_or_404(chapter.subject_id)
        questions = Question.query.filter_by(quiz_id=quiz_id).all()
        score = 0
        results = []
        total_correct_answer = 0
        for question in questions:
            user_answer = request.form.get(f'question_{question.id}')
            is_correct = user_answer == question.correct_option
            if is_correct:
                total_correct_answer += 1
                score += 1
            results.append({
                'question': question.question_title,
                'user_answer': user_answer,
                'correct_answer': question.correct_option,
                'is_correct': is_correct
            })
        total_questions = len(questions)
        percentage_score = round((score / total_questions) * 100, 1) if total_questions > 0 else 0

        new_score = Score(
            quiz_id=quiz.id,
            user_id=user_id,
            total_scored=score,
            percentage_score=percentage_score,
            subject_name=subject.subject_name,
            chapter_name=chapter.chapter_name,
            total_questions=total_questions,
            total_correct_answer=total_correct_answer
        )
        try:
            db.session.add(new_score)
            db.session.commit()
            return render_template('quiz_result.html',
                                   user=user,
                                   quiz=quiz,
                                   score=score,
                                   total_questions=total_questions,
                                   percentage_score=percentage_score,
                                   results=results)
        except Exception as e:
            db.session.rollback()
            print(f"Error submit quiz: {e}")
            return render_template('question.html', quiz_id=quiz_id)
    else:
        if 'user_id' not in session:
            return redirect('/')
        else:
            user_id = session['user_id']
            user = User.query.get(user_id)
            return render_template('user_profile.html', user=user)
