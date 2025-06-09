from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import datetime


db=SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer , primary_key=True , autoincrement=True)
    username = db.Column(db.String(100), unique=True , nullable = False)
    password = db.Column(db.String(200), nullable = False)
    role = db.Column(db.String(20), nullable = False )
    designation = db.Column(db.String, nullable = True)
    department = db.Column(db.String(100), nullable = False)

class RequestModel(db.Model):
    id = db.Column(db.Integer , primary_key=True , autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    user = db.relationship('User', backref='requests')
    item = db.Column(db.String(100), nullable = False)
    quantity = db.Column(db.Integer , nullable=True)
    remarks = db.Column(db.String(200), nullable=True)
    date_requested = db.Column(db.DateTime, default=datetime.now)
    status = db.Column(db.String(20) , default ='Pending')
    quantity_issued = db.Column(db.Integer, nullable = True)
