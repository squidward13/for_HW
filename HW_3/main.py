from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import CSRFProtect
from forms import RegistrationForm
from models import db, User
from hashlib import sha256

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'
app.config['SECRET_KEY'] = b'fefuhf7382f8y63tfgy682tfg3yfoa6gt3of6tr35frt7t2gf763tgf6tg'

csrf = CSRFProtect(app)

db.init_app(app)

@app.cli.command('init-db')
def db_init():
    db.create_all()

@app.route('/')
def index():
    return render_template('base.html')

@app.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit()
        db.session.add(User(name=form.name.data,
                            email=form.email.data, 
                            password=sha256(form.password.data.encode(encoding='utf-8')).hexdigest()))
        db.session.commit()
        return redirect(url_for('register'))
    return render_template('register.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)