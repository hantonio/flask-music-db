# app.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///music.db'
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
app.secret_key = "mysecretkey"

db = SQLAlchemy(app)
db.create_all()
db.session.commit()

admin = Admin(app, name="Admin Dashboard", template_mode='bootstrap3')