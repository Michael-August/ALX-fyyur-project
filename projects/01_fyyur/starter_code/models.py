from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Shows(db.Model):
	__tablename__ = 'shows'

	venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), primary_key=True)
	artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), primary_key=True)
	start_time = db.Column('start_time', db.DateTime)
	venue = db.relationship('Venue', backref='artists')
	artist = db.relationship('Artist', backref='venues')

class Venue(db.Model):
	__tablename__ = 'Venue'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String)
	city = db.Column(db.String(120))
	state = db.Column(db.String(120))
	address = db.Column(db.String(120))
	genres = db.Column(db.String(120)) 
	image_link = db.Column(db.String(500))
	facebook_link = db.Column(db.String(120))
	website_link = db.Column(db.String(100))
	seeking_talent = db.Column(db.Boolean, nullable=True)
	seeking_description = db.Column(db.String(1000))
	phone = db.Column(db.String(120))
	artist = db.relationship('Shows', backref='venues')

class Artist(db.Model):
	__tablename__ = 'Artist'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String)
	city = db.Column(db.String(120))
	state = db.Column(db.String(120))
	phone = db.Column(db.String(120))
	genres = db.Column(db.String(120))
	image_link = db.Column(db.String(500))
	facebook_link = db.Column(db.String(120))
	website_link = db.Column(db.String(200))
	seeking_venue = db.Column(db.Boolean)
	seeking_description = db.Column(db.String(200))
	venue = db.relationship('Shows', backref='artists')
