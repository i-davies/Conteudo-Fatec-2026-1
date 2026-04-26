import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Usa um arquivo SQLite dentro da pasta deste projeto
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "banco.sqlite")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
