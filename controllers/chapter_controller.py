from flask import Blueprint, request, redirect, render_template, session

from models import db, Subject, Chapter, User

chapter_controller = Blueprint('chapter_controller', __name__)


@chapter_controller.route('/chapters/<int:subject_id>')
def chapters(subject_id):
    if 'user_id' not in session:
        return redirect('/')
    else:
        user_id = session['user_id']
        user = User.query.get(user_id)
        subject = Subject.query.get_or_404(subject_id)
        return render_template("chapters.html", subject=subject, user=user)


@chapter_controller.route('/create-chapter/<int:subject_id>', methods=['GET', 'POST'])
def create_chapter(subject_id):
    if request.method == 'POST':
        chapter_name = request.form["name"]
        chapter_desc = request.form["description"]
        new_chapter = Chapter(chapter_name=chapter_name,
                              chapter_description=chapter_desc,
                              subject_id=subject_id)
        try:
            db.session.add(new_chapter)
            db.session.commit()
            return redirect('/chapters/' + str(subject_id))
        except Exception as e:
            db.session.rollback()
            print(f"Error create chapter: {e}")
            subject = Subject.query.get_or_404(subject_id)
            return render_template("create_chapter.html", subject=subject)
    else:
        subject = Subject.query.get_or_404(subject_id)
        return render_template("create_chapter.html", subject=subject)


@chapter_controller.route('/delete-chapter/<int:chapter_id>', methods=['GET', 'POST'])
def delete_chapter(chapter_id):
    if request.method == 'POST':
        chapter = Chapter.query.get(chapter_id)
        subject_id = chapter.subject_id
        try:
            db.session.delete(chapter)
            db.session.commit()
            return redirect('/chapters/' + str(subject_id))
        except Exception as e:
            db.session.rollback()
            print(f"Error delete chapter: {e}")
            return redirect('/chapters/' + str(subject_id))


@chapter_controller.route('/edit-chapter/<int:chapter_id>', methods=['GET', 'POST'])
def edit_chapter(chapter_id):
    if request.method == 'POST':
        chapter = Chapter.query.get(chapter_id)
        subject_id = chapter.subject_id
        chap_name = request.form['name']
        chap_desc = request.form['chapter_description']
        chapter.chapter_name = chap_name
        chapter.chapter_description = chap_desc
        chapter.subject_id = subject_id
        try:
            db.session.commit()
            return redirect('/chapters/' + str(subject_id))
        except Exception as e:
            db.session.rollback()
            print(f"Error edit chapter: {e}")
            chapter = Chapter.query.get(chapter_id)
            return render_template("edit_chapter.html", chapter=chapter)
    else:
        chapter = Chapter.query.get(chapter_id)
        return render_template("edit_chapter.html", chapter=chapter)
