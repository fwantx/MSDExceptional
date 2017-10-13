import os
import json
import datetime
from datetime import date
from flask import Flask, jsonify, Response, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
import utils

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:////tmp/test.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
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
    name = db.Column(db.String(255), unique=True)
    city_id = db.Column(db.Integer, nullable=False)
    location_x = db.Column(db.Integer, nullable=False)
    location_y = db.Column(db.Integer, nullable=False)
    kennel_num = db.Column(db.Integer, nullable=False)
    empty_kennel_num = db.Column(db.Integer, nullable=False)
    pets = db.relationship('Pet', backref='pet', lazy=True)

    def __init__(self, name, city_id, location_x, location_y, kennel_num):
        self.name = name
        self.city_id = city_id
        self.location_x = location_x
        self.location_y = location_y
        self.kennel_num = kennel_num
        self.empty_kennel_num = kennel_num

    def __repr__(self):
        return '<Shelter %r>' % self.name


# class GenderType(enum.Enum):
#     MALE = "Male"
#     FEMALE = "Female"


class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    color = db.Column(db.String(80), nullable=False)
    type = db.Column(db.String(80), nullable=False)
    breed = db.Column(db.String(80), nullable=False)
    size = db.Column(db.Integer, nullable=False)
    # gender = db.Column(enum.Enum(GenderType), nullable=False)
    gender = db.Column(db.String(80), nullable=False)
    shelter_id = db.Column(db.Integer, db.ForeignKey('shelter.id'), nullable=True)
    found_time = db.Column(db.Date, nullable=False)
    found_location_x = db.Column(db.Integer, nullable=False)
    found_location_y = db.Column(db.Integer, nullable=False)

    def __init__(self, color, type, breed, size, gender, found_time, found_location_x, found_location_y,
                 shelter_id=None):
        self.color = color
        self.type = type
        self.breed = breed
        self.size = size
        self.gender = gender
        self.found_time = found_time
        self.found_location_x = found_location_x
        self.found_location_y = found_location_y
        self.shelter_id = shelter_id

    def __repr__(self):
        return '<Pet %r>' % self.id


if __name__ == '__main__':
    db.create_all()


@app.route("/test")
def test():
    color = request.args.get('color')
    type = request.args.get('type')
    breed = request.args.get('breed')
    size = request.args.get('size')
    gender = request.args.get('gender')
    found_location_x = request.args.get('x')
    found_location_y = request.args.get('y')
    new_pet = Pet(color, type, breed, size, gender, date.today(), found_location_x, found_location_y)
    db.session.add(new_pet)
    db.session.commit()
    return jsonify(success='yes')


@app.route("/createpet")
def create_pet():
    color = request.args.get('color')
    type = request.args.get('type')
    breed = request.args.get('breed')
    size = request.args.get('size')
    gender = request.args.get('gender')
    found_location_x = request.args.get('x')
    found_location_y = request.args.get('y')
    new_pet = Pet(color, type, breed, size, gender, date.today(), found_location_x, found_location_y)
    db.session.add(new_pet)
    db.session.commit()
    return jsonify(success='yes')


@app.route("/assignshelter")
def assign_shelter():
    shelter_id = request.args.get('shelterid')
    pet_id = request.args.get('petid')
    # pet_num = db.session.query(Pet).filter_by(shelter_id = shelter_id).count()
    # this_shelter = Shelter.query.filter_by(id=shelter_id).first()
    this_shelter = Shelter.query.get(shelter_id)
    this_pet = Pet.query.get(pet_id)
    if this_shelter.empty_kennel_num > 0:
        this_pet.shelter_id = shelter_id
        this_shelter.empty_kennel_num -= 1
        return jsonify(ShelterName=this_shelter.name)
    else:
        # Assume that there must be at least one available shelter
        another_shelter = Shelter.query.order_by(Shelter.empty_kennel_num.desc()).first()
        this_pet.shelter_id = another_shelter.id
        another_shelter.empty_kennel_num -= 1
        return jsonify(ShelterName=another_shelter.name)
    db.session.commit()


@app.route("/search")
def search_pet():
    location_x = int(request.args.get('x'))
    location_y = int(request.args.get('y'))
    radius = int(request.args.get('r'))
    boundx1 = location_x - radius
    boundx2 = location_x + radius
    boundy1 = location_y - radius
    boundy2 = location_y + radius
    # def check_pos(x, y):
    #     if (boundx1 < x < boundx2) is True and (boundy1 < y < boundy2) is True:
    #         return True
    #     else:
    #         return False


    pets = Pet.query.filter(and_(Pet.found_location_x > boundx1,
											 Pet.found_location_x < boundx2,
											 Pet.found_location_y > boundy1,
											 Pet.found_location_y < boundy2)).all()
    list = [pet.id for pet in pets]
    return jsonify(results=list)


@app.route("/")
def hello():
	admin = User.query.filter_by(username='admin').first()
	return jsonify(username=admin.username,
			email=admin.email,
			id=admin.id) 

@app.route("/getCities")
@utils.crossdomain(origin='*')
def getCities():
	cities = City.query.all()
	# https://stackoverflow.com/questions/21411497/flask-jsonify-a-list-of-objects
	return jsonify([city.serialize() for city in cities])

@app.route("/getSheltersByCity")
def getShelterByCity():
	cities = City.query.all()
	return jsonify(
		{
			city.name: [
				shelter.serialize() for shelter in city.shelters
			] for city in cities
		}
	)






