import uuid

from flask_sqlalchemy import SQLAlchemy
from app import db
from sqlalchemy.dialects.postgresql import JSON

# db = SQLAlchemy()


class User(db.Model):
   id = db.Column(db.String(), primary_key=True, default=lambda: str(uuid.uuid4()))
   username = db.Column(db.String())
   email = db.Column(db.String(), unique=True)

class Result(db.Model):
   __tablename__ = 'results'

   id = db.Column(db.Integer, primary_key=True)
   url = db.Column(db.String())
   result_all = db.Column(JSON)
   result_no_stop_words = db.Column(JSON)

   def __init__(self, url, result_all, result_no_stop_words):
      self.url = url
      self.result_all = result_all
      self.result_no_stop_words = result_no_stop_words

   def __repr__(self):
      return '<id {}>'.format(self.id)

