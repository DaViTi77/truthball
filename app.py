import os
from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

# ------------------------------------------------------------------
# 🛠️ აპლიკაციის და ბაზის კონფიგურაცია
# ------------------------------------------------------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_super_secret_key_123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///truthball.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# ------------------------------------------------------------------
# 🗄️ მონაცემთა ბაზის მოდელები (Models)
# ------------------------------------------------------------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

class Transfer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_name = db.Column(db.String(150), nullable=False)
    from_club = db.Column(db.String(150), nullable=False)
    to_club = db.Column(db.String(150), nullable=False)
    fee_millions = db.Column(db.String(100), nullable=False)
    contract_years = db.Column(db.String(100), nullable=False)
    source = db.Column(db.String(150), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ------------------------------------------------------------------
# 📋 ფორმების კლასები (WTForms)
# ------------------------------------------------------------------
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('შესვლა')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('რეგისტრაცია')

class TransferForm(FlaskForm):
    player_name = StringField('Player Name', validators=[DataRequired()])
    from_club = StringField('From Club', validators=[DataRequired()])
    to_club = StringField('To Club', validators=[DataRequired()])
    fee_millions = StringField('Fee Millions', validators=[DataRequired()])
    contract_years = StringField('Contract Years', validators=[DataRequired()])
    source = StringField('Source', validators=[DataRequired()])
    submit = SubmitField('Submit')

# ------------------------------------------------------------------
# 🛣️ საიტის მარშრუტები (Routes)
# ------------------------------------------------------------------

@app.route('/')
def index():
    transfers = Transfer.query.order_by(Transfer.id.desc()).all()
    return render_template('index.html', transfers=transfers)

@app.route('/add_transfer', methods=['GET', 'POST'])
@login_required
def add_transfer():
    form = TransferForm()
    
    if form.validate_on_submit():
        new_transfer = Transfer(
            player_name=form.player_name.data,
            from_club=form.from_club.data,
            to_club=form.to_club.data,
            fee_millions=form.fee_millions.data,
            contract_years=form.contract_years.data,
            source=form.source.data
        )
        db.session.add(new_transfer)
        db.session.commit()
        return redirect(url_for('index'))
        
    return render_template('add_transfer.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            return redirect(url_for('index'))
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if not existing_user:
            # ავტომატურად ვსვამთ True-ზე, რომ ახალ იუზერს ჰქონდეს ადმინ პანელი
            new_user = User(username=form.username.data, password=form.password.data, is_admin=True)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('index'))
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# ------------------------------------------------------------------
# 🚀 აპლიკაციის გაშვება და ბაზის შექმნა
# ------------------------------------------------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)