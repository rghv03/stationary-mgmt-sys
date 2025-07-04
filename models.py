from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import JSON, func
from datetime import datetime


db=SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer , primary_key=True , autoincrement=True)
    username = db.Column(db.String(100), unique=True , nullable = False)
    password = db.Column(db.String(200), nullable = False)
    role = db.Column(db.String(20), nullable = False )
    designation = db.Column(db.String, nullable = True)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable = False)
    department = db.relationship('Department',foreign_keys=[department_id], backref='users')

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

class MonthlyRequest(db.Model):
    id = db.Column(db.Integer , primary_key=True , autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    user = db.relationship('User', backref='monthly_requests')
    month = db.Column(db.String(20), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    items = db.Column(JSON)
    date_requested = db.Column(db.DateTime, default=datetime.now)
    ad_status = db.Column(db.String(20), default='Pending')
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    department = db.relationship('Department', foreign_keys=[department_id])

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    shortname = db.Column(db.String(50), unique=True, nullable=False)
    head_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    ad_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    head = db.relationship('User', foreign_keys=[head_id], backref='headed_departments')
    ad = db.relationship('User', foreign_keys=[ad_id], backref='ad_departments')


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group = db.ForeignKey('group.name')
    stationary_incharge = db.Column(db.String(100), nullable=False)
