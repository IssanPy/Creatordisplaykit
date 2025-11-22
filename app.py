import os
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import UserMixin, LoginManager, login_user, logout_user, current_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY','dev-secret')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR,'portfolio.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)

class Creator(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(255))
    name = db.Column(db.String(120))

class Work(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    description = db.Column(db.Text)
    media_url = db.Column(db.String(255))

class WorkForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    media_url = StringField('Media URL')
    submit = SubmitField('Save')

@login.user_loader
def load_user(uid):
    return Creator.query.get(int(uid))

@app.route('/')
def index():
    works = Work.query.all()
    return render_template('index.html', works=works)

@app.route('/admin', methods=['GET','POST'])
@login_required
def admin_panel():
    form = WorkForm()
    if form.validate_on_submit():
        w = Work(title=form.title.data, description=form.description.data, media_url=form.media_url.data)
        db.session.add(w)
        db.session.commit()
        flash('Saved', 'success')
        return redirect(url_for('admin_panel'))
    works = Work.query.all()
    return render_template('admin.html', form=form, works=works)

@app.cli.command('create-creator')
def create_creator():
    e = input('email: ')
    n = input('name: ')
    p = input('password: ')
    if Creator.query.filter_by(email=e).first():
        print('exists')
        return
    c = Creator(email=e, name=n, password=p)
    db.session.add(c)
    db.session.commit()
    print('created')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
