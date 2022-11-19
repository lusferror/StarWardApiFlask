from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

FavoritesPeoples=db.Table('FavoritesPeoples',
    db.Column('user_id',db.Integer,db.ForeignKey('user.id'), primary_key=True),
    db.Column('people_id',db.Integer,db.ForeignKey('people.id'), primary_key=True))

FavoritesPlanets=db.Table('FavoritesPlanets',
    db.Column('user_id',db.Integer,db.ForeignKey('user.id'), primary_key=True),
    db.Column('planet_id',db.Integer,db.ForeignKey('planets.id'), primary_key=True))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)
    favoritesPeople=db.relationship('People',secondary=FavoritesPeoples,backref=db.backref('users',lazy=True))
    favoritesPeople=db.relationship('Planets',secondary=FavoritesPlanets,backref=db.backref('users',lazy=True))
    

    def __repr__(self):
        return '<User %r>' % self.username


    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }

class Planets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=False, nullable=False)
    url = db.Column(db.String(100), unique=False, nullable=False)
    uid = db.Column(db.String(100), unique=False, nullable=False)

    def serialize(self):
        return{
            "uid":self.id,
            "name":self.name,
            "url":self.url
        }

class People(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=False, nullable=False)
    url = db.Column(db.String(100), unique=False, nullable=False)
    uid = db.Column(db.String(100), unique=False, nullable=False)
    def serialize(self):
        return{
            "uid":self.id,
            "name":self.name,
            "url":self.url
        }
    
