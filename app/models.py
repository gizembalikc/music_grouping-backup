# -*- coding: utf-8 -*-
"""
Created on Thu Apr 29 22:37:30 2021

@author: gizem
"""
#from datetime import datetime
from app import db
from app import login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin,db.Model):
    #db.Column takes the field type as an argument, plus other optional arguments
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    #posts = db.relationship('Post', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username) 
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self,password):
        return check_password_hash(self.password_hash, password)


#The user loader is registered with Flask-Login with the @login.user_loader decorator. 
#The id that Flask-Login passes to the function as an argument is going to be a string, 
#so databases that use numeric IDs need to convert the string to integer 
@login.user_loader
def load_user(id):
    return User.query.get(int(id))

        
#TODO: Groupingi boyle direkt database kaydetmece?
#class Post(db.Model):
#    id = db.Column(db.Integer, primary_key=True)
#    body = db.Column(db.String(140))
#    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
#    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#
#    def __repr__(self):
#        return '<Post {}>'.format(self.body)