from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(256), nullable=False)
    qualification = db.Column(db.String(80), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_flagged = db.Column(db.Boolean, default=False)


class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_name = db.Column(db.String(150), unique=True)
    subject_description = db.Column(db.String(500), nullable=False)
    chapters = db.relationship("Chapter", backref="subject", cascade="all, delete-orphan", passive_deletes=True)


class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chapter_name = db.Column(db.String(150), nullable=False)
    chapter_description = db.Column(db.String(150), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id", ondelete="CASCADE"), nullable=False)
    quizzes = db.relationship("Quiz", backref="chapter", cascade="all, delete-orphan", passive_deletes=True)


class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_name = db.Column(db.String(150), nullable=False)
    quiz_duration = db.Column(db.String(5), nullable=False)
    quiz_date = db.Column(db.Date, nullable=False)
    quiz_remark = db.Column(db.String(150), nullable=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey("chapter.id", ondelete="CASCADE"), nullable=False)
    questions = db.relationship("Question", backref="quiz", cascade="all, delete-orphan", passive_deletes=True)


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_title = db.Column(db.String(500), nullable=False)
    option_a = db.Column(db.String(100), nullable=False)
    option_b = db.Column(db.String(100), nullable=False)
    option_c = db.Column(db.String(100), nullable=False)
    option_d = db.Column(db.String(100), nullable=False)
    correct_option = db.Column(db.String(1), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id', ondelete="CASCADE"), nullable=False)


class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id', ondelete="CASCADE"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    time_stamp_of_attempt = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    total_scored = db.Column(db.Integer, nullable=False)
    percentage_score = db.Column(db.Float, nullable=False)
    subject_name = db.Column(db.String(100), nullable=False)
    chapter_name = db.Column(db.String(100), nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    total_correct_answer = db.Column(db.Integer, nullable=False)
    quiz = db.relationship('Quiz', backref='scores')
    user = db.relationship('User', backref='scores')
