import json
import unittest
from hello import app, db, City, Shelter, Pet

class PetTestCase(unittest.TestCase):

	def setUp(self):
		db.drop_all()
		db.create_all()
		app.testing = True
		self.app = app.test_client()

	def tearDown(self):
		pass

	def addOnePet(self):
		pet = Pet("Java", "male", "white", "dog", "husky", 10, 1, 1)
		db.session.add(pet)
		db.session.commit()

	def addOneShelter(self):
		city = City("Seattle")
		shelter = Shelter("SLUShelter", 100, city, 1, 1)
		db.session.add(shelter)
		db.session.commit()

	def test_pets(self):
		pet = Pet("Java", "male", "white", "dog", "husky", 10, 1, 1)
		ret = self.app.post('/pets', data=json.dumps(pet.serialize()), content_type='application/json')
		assert ret.status_code == 201
		assert b'"name": "Java"' in ret.data

	def test_pets_petId_get(self):
		self.addOnePet()
		ret = self.app.get('/pets/1')
		assert ret.status_code == 200
		assert b'"name": "Java"' in ret.data

	def test_pets_petId_put(self):
		self.addOnePet()
		pet = Pet("Python", "male", "white", "dog", "husky", 10, 1, 1)
		ret = self.app.put('/pets/1', data=json.dumps(pet.serialize()), content_type='application/json')
		assert ret.status_code == 200
		assert b'"name": "Python"' in ret.data

	def test_pets_petId_delete(self):
		self.addOnePet()
		ret = self.app.delete('/pets/1')
		assert ret.status_code == 200
		assert b'deleted successfully' in ret.data

	def test_shelters_shelterId_pets_post(self):
		self.addOneShelter()
		pet = Pet("Python", "male", "white", "dog", "husky", 10, 1, 1)
		ret = self.app.post('/shelters/1/pets', data=json.dumps(pet.serialize()), content_type='application/json')
		assert ret.status_code == 201
		assert b'"name": "SLUShelter"' in ret.data

	def test_shelters_shelterId_pets_get(self):
		pet1 = Pet("Java", "male", "white", "dog", "husky", 10, 1, 1)
		pet2 = Pet("Python", "male", "white", "dog", "husky", 10, 1, 1)
		self.addOneShelter()
		ret = self.app.post('/shelters/1/pets', data=json.dumps(pet1.serialize()), content_type='application/json')
		ret = self.app.post('/shelters/1/pets', data=json.dumps(pet2.serialize()), content_type='application/json')
		ret = self.app.get('/shelters/1/pets')
		assert ret.status_code == 200
		assert b'"name": "Java"' in ret.data
		assert b'"name": "Python"' in ret.data

if __name__ == '__main__':
	unittest.main()