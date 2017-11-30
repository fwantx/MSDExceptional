# Test Code Review

import os
import json
import datetime
from datetime import date
from flask import Flask, jsonify, Response, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import and_, func
import utils

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    if (config_name == 'testing'):
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:////tmp/test.db')
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:////tmp/development.db')
        # app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:931028hmh@localhost:3306/PetTracking'

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
    def welcome():
        return 'Welcome to Exceptional!'

    @app.route("/cities", methods=['GET', 'POST'])
    @utils.crossdomain(origin='*')
    def cities():
        if request.method == 'POST':
            name = request.get_json().get('name')
            city = City(name=name)
            city.save()
            response = jsonify(city.serialize())
            response.status_code = 201
        else:
            cities = City.query.all()
            # https://stackoverflow.com/questions/21411497/flask-jsonify-a-list-of-objects
            response = jsonify([city.serialize() for city in cities])
            response.status_code = 200
        return response

    @app.route("/cities/<int:id>", methods=['GET', 'PUT', 'DELETE'])
    @utils.crossdomain(origin='*')
    def city_operation(id, **kwargs):
        city = City.query.filter_by(id=id).first()
        if not city:
            abort(404)
        if request.method == 'DELETE':
            city.delete()
            response = jsonify(
                {
                    "message": "city {} deleted successfully".format(city.id)
                }
            )
            response.status_code = 200
        elif request.method == 'PUT':
            name = request.get_json().get('name')
            city.name = name
            city.save()
            response = jsonify(city.serialize())
            response.status_code = 200
        else:
            response = jsonify(city.serialize())
            response.status_code = 200
        return response

    @app.route("/cities/<int:id>/shelters", methods=['GET', 'POST'])
    @utils.crossdomain(origin='*')
    def shelters_by_city(id, **kwargs):
        city = City.query.filter_by(id=id).first()
        if not city:
            abort(404)
        if request.method == 'POST':
            params = request.get_json()
            shelter = Shelter(params['name'], params['kennel_num'], params['location_x'], params['location_y'], city)
            shelter.save()
            response = jsonify(shelter.serialize())
            response.status_code = 201
        else:
            shelters = city.shelters
            response = jsonify([shelter.serialize() for shelter in shelters])
            response.status_code = 200
        return response

    @app.route("/shelters/<int:id>", methods=['GET', 'PUT', 'DELETE'])
    @utils.crossdomain(origin="*")
    def shelter_operation(id, **kwargs):
        shelter = Shelter.query.filter_by(id=id).first()
        if not shelter:
            abort(404)
        if request.method == 'DELETE':
            shelter.delete()
            response = jsonify(
                {
                    "message": "shelter {} deleted successfully".format(shelter.id)
                }
            )
            response.status_code = 200
        elif request.method == 'PUT':
            params = request.get_json()
            shelter.name = params.get('name', shelter.name)
            shelter.kennel_num = params.get('kennel_num', shelter.kennel_num)
            shelter.city_id = params.get('city_id', shelter.city_id)
            shelter.location_x = params.get('location_x', shelter.location_x)
            shelter.location_y = params.get('location_y', shelter.location_y)
            shelter.save()
            response = jsonify(shelter.serialize())
            response.status_code = 200
        else:
            response = jsonify(shelter.serialize())
            response.status_code = 200
        return response

    @app.route("/shelters/<int:id>/pets", methods=['GET', 'POST'])
    @utils.crossdomain(origin="*")
    def pets_by_shelter(id, **kwargs):
        shelter = Shelter.query.filter_by(id=id).first()
        if not shelter:
            abort(404)
        if request.method == 'POST':
            params = request.get_json()
            pet = Pet(params['name'], params['gender'], params['color'], params['type'], params['breed'], params['size'], params['found_location_x'], params['found_location_y'], shelter)
            pet.save()
            response = jsonify(pet.serialize())
            response.status_code = 201
            # def __init__(self, name, gender, color, type, breed, size, found_location_x, found_location_y, shelter=None):
        else:
            pets = shelter.pets
            response = jsonify([pet.serialize() for pet in pets])
            response.status_code = 200
        return response

    @app.route("/pets/<int:id>", methods=['GET', 'PUT', 'DELETE'])
    @utils.crossdomain(origin="*")
    def pet_operation(id, **kwargs):
        pet = Pet.query.filter_by(id=id).first()
        if not pet:
            abort(404)
        if request.method == 'DELETE':
            pet.delete()
            response = jsonify(
                {
                    "message": "pet {} deleted successfully".format(pet.id)
                }
            )
            response.status_code = 200
        elif request.method == 'PUT':
            params = request.get_json()
            pet.name = params.get('name', pet.name)
            pet.gender = params.get('gender', pet.gender)
            pet.color = params.get('color', pet.color)
            pet.type = params.get('type', pet.type)
            pet.breed = params.get('breed', pet.breed)
            pet.size = params.get('size', pet.size)
            pet.found_location_x = params.get('found_location_x', pet.found_location_x)
            pet.found_location_y = params.get('found_location_y', pet.found_location_y)
            pet.shelter_id = params.get('shelter_id', pet.shelter_id)
            pet.save()
            response = jsonify(pet.serialize())
            response.status_code = 200
        else:
            response = jsonify(pet.serialize())
            response.status_code = 200
        return response

    @app.route("/search_pets", methods=['GET'])
    @utils.crossdomain(origin="*")
    def search_pets():
        if request.method != 'GET':
            abort(404)
        else:
            params = request.args
            conditions = dict()
            if 'gender' in params:
                conditions['gender'] = params.get('gender')
            if 'color' in params:
                conditions['color'] = params.get('color')
            if 'type' in params:
                conditions['type'] = params.get('type')
            if 'breed' in params:
                conditions['breed'] = params.get('breed')
            if 'size' in params:
                conditions['size'] = int(params.get('size'))
            if 'shelter_id' in params:
                conditions['shelter_id'] = int(params.get('shelter_id'))
            if 'found_location_x' not in params or 'found_location_y' not in params:
                pets = Pet.query.filter_by(**conditions).all()
            else:
                x_lower = int(params.get('found_location_x')) - 3
                x_upper = int(params.get('found_location_x')) + 3
                y_lower = int(params.get('found_location_y')) - 3
                y_upper = int(params.get('found_location_y')) + 3
                pets = Pet.query.filter_by(**conditions).filter(
                    Pet.found_location_x >= x_lower,
                    Pet.found_location_x <= x_upper,
                    Pet.found_location_y >= y_lower,
                    Pet.found_location_y <= y_upper,
                ).all()
            response = jsonify([p.serialize() for p in pets])
            response.status_code = 200
        return response

    @app.route("/search_available_shelters", methods=['GET'])
    @utils.crossdomain(origin="*")
    def search_available_shelters():
        if request.method != 'GET':
            abort(404)
        else:
            params = request.args
            if 'found_location_x' not in params or 'found_location_y' not in params:
                shelters = Shelter.query.join(Pet).group_by(Shelter).having(func.count(Pet.id) < Shelter.kennel_num).all()
            else:
                x_lower = int(params.get('found_location_x')) - 10
                x_upper = int(params.get('found_location_x')) + 10
                y_lower = int(params.get('found_location_y')) - 10
                y_upper = int(params.get('found_location_y')) + 10
                shelters = Shelter.query.join(Pet).group_by(Shelter).having(func.count(Pet.id) < Shelter.kennel_num).filter(
                    Shelter.location_x >= x_lower,
                    Shelter.location_x <= x_upper,
                    Shelter.location_y >= y_lower,
                    Shelter.location_y <= y_upper,
                ).all()
                print(shelters)
            response = jsonify([s.serialize() for s in shelters])
            response.status_code = 200
        return response

    @app.route("/pets", methods=['POST'])
    @utils.crossdomain(origin="*")
    def pet_post():
        params = request.get_json()
        name = params.get('name')
        gender = params.get('gender')
        color = params.get('color')
        type = params.get('type')
        breed = params.get('breed')
        size = params.get('size')
        found_location_x = params.get('found_location_x')
        found_location_y = params.get('found_location_y')
        pet = Pet(name, gender, color, type, breed, size, found_location_x, found_location_y)
        pet.save()
        response = jsonify(pet.serialize())
        response.status_code = 201

        return response

    return app

app = create_app(config_name='development')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Base(object):
    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class City(db.Model, Base):
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

class Shelter(db.Model, Base):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    kennel_num = db.Column(db.Integer, nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'))
    city = db.relationship('City', backref=db.backref('shelters', lazy='dynamic'))
    location_x = db.Column(db.Integer, nullable=False)
    location_y = db.Column(db.Integer, nullable=False)    

    def __init__(self, name, kennel_num, location_x, location_y, city=None):
        self.name = name
        self.kennel_num = kennel_num
        self.location_x = location_x
        self.location_y = location_y
        self.city = city

    def __repr__(self):
        return '<Shelter %r>' % self.name

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'kennel_num': self.kennel_num,
            'city': self.city.serialize() if self.city else None,
            'location_x': self.location_x,
            'location_y': self.location_y,
        }

class Pet(db.Model, Base):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    color = db.Column(db.String(80), nullable=False)
    type = db.Column(db.String(80), nullable=False)
    breed = db.Column(db.String(80), nullable=False)
    size = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(80), nullable=False)
    shelter_id = db.Column(db.Integer, db.ForeignKey('shelter.id'), nullable=True)
    shelter = db.relationship('Shelter', backref=db.backref('pets', lazy='dynamic'))
    found_time = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    found_location_x = db.Column(db.Integer, nullable=False)
    found_location_y = db.Column(db.Integer, nullable=False)

    def __init__(self, name, gender, color, type, breed, size, found_location_x, found_location_y, shelter=None):
        self.name = name
        self.gender = gender
        self.color = color
        self.type = type
        self.breed = breed
        self.size = size
        self.found_location_x = found_location_x
        self.found_location_y = found_location_y
        self.shelter = shelter

    def __repr__(self):
        return '<Pet %r>' % self.id

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'gender': self.gender,
            'color': self.color,
            'type': self.type,
            'breed': self.breed,
            'size': self.size,
            'found_location_x': self.found_location_x,
            'found_location_y': self.found_location_y,
            'shelter': self.shelter.serialize() if self.shelter else None,
        }
