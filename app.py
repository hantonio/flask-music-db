# app.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///music.db'
app.secret_key = "mysecretkey"

db = SQLAlchemy(app)

db.create_all()
db.session.commit()
