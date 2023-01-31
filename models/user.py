from db import db


class UserModel(db.Model):
    __tablename__="users"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(20), nullable=False)
    