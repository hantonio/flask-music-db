# app.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///music.db'
app.secret_key = "mysecretkey"

Bootstrap(app)

db = SQLAlchemy(app)
db.create_all()
db.session.commit()

admin = Admin(app, name="Admin Dashboard", template_mode='bootstrap3')