import os
import json
from flask import Flask, jsonify, Response
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:////tmp/test.db') 
db = SQLAlchemy(app)

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True)
	email = db.Column(db.String(120), unique=True)

	def __init__(self, username, email):
		self.username = username
		self.email = email
	
	def __repr__(self):
		return '<User %r>' % self.username

class City(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(255))

	def __init__(self, name):
		self.name = name

	def __repr__(self):
		return '<City %r>' % self.name

	def serialize(self):
		return {
			'id': self.id,
			'name': self.name,
		}

class Shelter(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(255))
	capacity = db.Column(db.Integer)
	city_id = db.Column(db.Integer, db.ForeignKey('city.id'))
	city = db.relationship('City', backref=db.backref('shelters', lazy='dynamic'))

	def __init__(self, name, capacity, city):
		self.name = name
		self.capacity = capacity
		self.city = city

	def __repr__(self):
		return '<Shelter %r>' % self.name




@app.route("/")
def hello():
	admin = User.query.filter_by(username='admin').first()
	return jsonify(username=admin.username,
			email=admin.email,
			id=admin.id) 

@app.route("/getCities")
def getCities():
	cities = City.query.all()
	# https://stackoverflow.com/questions/21411497/flask-jsonify-a-list-of-objects
	return jsonify([e.serialize() for e in cities])


