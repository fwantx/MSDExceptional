import json
import unittest
from hello import create_app, db, City, Shelter, Pet, User

class HelloTestCase(unittest.TestCase):

	def setUp(self):
		self.app = create_app(config_name='testing')
		self.app.testing = True
		self.client = self.app.test_client()
		self.city_1 = City('Seattle')
		self.city_2 = City('Boston')
		self.shelter_1 = Shelter('Northgate Pet Center', 3, 10, 10)
		self.shelter_2 = Shelter('Westlake Animal Center', 2, 20, 20)
		self.shelter_3 = Shelter('UW Animal Center', 20, 150, 20)
		self.pet_1 = Pet("Dog 1", "male", "white", "dog", "husky", 10, 21, 22)
		self.pet_2 = Pet("Dog 2", "male", "yellow", "dog", "chihuahua", 10, 10, 10)
		self.pet_3 = Pet("Dog 3", "female", "white", "dog", "husky", 5, 20, 20)
		self.user_data = {
			'email': 'test@example.com',
			'password': 'test_password',
		}
		self.not_user_data = {
			'email': 'not_a_user@example.com',
			'password': 'nope',
		}

		with self.app.app_context():
			db.drop_all()
			db.create_all()

	def tearDown(self):
		with self.app.app_context():
			db.session.remove()
			db.drop_all()

	def register_user(self, email='user@test.com', password='test1234'):
		user_data = {
			'email': email,
			'password': password,
		}
		return self.client.post('/auth/register', data=json.dumps(user_data), content_type='application/json')

	def login_user(self, email='user@test.com', password='test1234'):
		user_data = {
			'email': email,
			'password': password,
		}
		return self.client.post('/auth/login', data=json.dumps(user_data), content_type='application/json')

	def testRoot(self):
		result = self.register_user()
		result = self.login_user()
		access_token = json.loads(result.data.decode())['access_token']

		rv = self.client.get('/', headers=dict(Token=access_token))
		assert rv.status_code == 200
		assert 'Welcome to Exceptional!' in str(rv.data)

	def test_can_create_city(self):
		rv = self.client.post('/cities', data=json.dumps(self.city_1.serialize()), content_type='application/json')
		assert rv.status_code == 201
		assert self.city_1.name in str(rv.data)

	def test_can_query_all_cities(self):
		rv = self.client.post('/cities', data=json.dumps(self.city_1.serialize()), content_type='application/json')
		assert rv.status_code == 201
		assert self.city_1.name in str(rv.data)
		rv = self.client.get('/cities')
		assert rv.status_code == 200
		assert self.city_1.name in str(rv.data)

	def test_can_query_city_by_id(self):
		rv = self.client.post('/cities', data=json.dumps(self.city_1.serialize()), content_type='application/json')
		assert rv.status_code == 201
		assert self.city_1.name in str(rv.data)
		id = json.loads(rv.data.decode('utf-8').replace("'", "\""))['id']
		rv = self.client.get('/cities/{}'.format(id))
		assert rv.status_code == 200
		assert self.city_1.name in str(rv.data)

	def test_can_edit_city_by_id(self):
		rv = self.client.post('/cities', data=json.dumps(self.city_1.serialize()), content_type='application/json')
		assert rv.status_code == 201
		assert self.city_1.name in str(rv.data)
		id = json.loads(rv.data.decode('utf-8').replace("'", "\""))['id']
		rv = self.client.put('/cities/{}'.format(id), data=json.dumps(self.city_2.serialize()), content_type='application/json')
		assert rv.status_code == 200
		assert self.city_2.name in str(rv.data)
		rv = self.client.get('/cities/{}'.format(id))
		assert self.city_2.name in str(rv.data)

	def test_can_delete_city_by_id(self):
		rv = self.client.post('/cities', data=json.dumps(self.city_1.serialize()), content_type='application/json')
		assert rv.status_code == 201
		assert self.city_1.name in str(rv.data)
		id = json.loads(rv.data.decode('utf-8').replace("'", "\""))['id']
		rv = self.client.delete('/cities/{}'.format(id))
		assert rv.status_code == 200
		rv = self.client.get('/cities/{}'.format(id))
		assert rv.status_code == 404

	def test_can_create_shelter_with_city(self):
		rv = self.client.post('/cities', data=json.dumps(self.city_1.serialize()), content_type='application/json')
		assert rv.status_code == 201
		assert self.city_1.name in str(rv.data)

		rv = self.client.post('/cities/1/shelters', data=json.dumps(self.shelter_1.serialize()), content_type='application/json')
		assert rv.status_code == 201
		assert self.shelter_1.name in str(rv.data)

	def test_can_edit_shelter_by_id(self):
		rv = self.client.post('/cities', data=json.dumps(self.city_1.serialize()), content_type='application/json')
		assert rv.status_code == 201
		assert self.city_1.name in str(rv.data)
		rv = self.client.post('/cities/1/shelters', data=json.dumps(self.shelter_1.serialize()), content_type='application/json')
		assert rv.status_code == 201
		assert self.shelter_1.name in str(rv.data)
		rv = self.client.put('/shelters/1', data=json.dumps({'name': 'Small Animal Clinic'}), content_type='application/json')
		assert rv.status_code == 200
		rv = self.client.get('shelters/1')
		assert 'Small Animal Clinic' in str(rv.data)

	def test_can_create_pet_with_shelter(self):
		rv = self.client.post('/cities', data=json.dumps(self.city_1.serialize()), content_type='application/json')
		assert rv.status_code == 201
		assert self.city_1.name in str(rv.data)
		rv = self.client.post('/cities/1/shelters', data=json.dumps(self.shelter_1.serialize()), content_type='application/json')
		assert rv.status_code == 201
		assert self.shelter_1.name in str(rv.data)

	def test_can_search_pets(self):
		# create 3 pets for testing
		rv = self.client.post('/pets', data=json.dumps(self.pet_1.serialize()), content_type='application/json')
		assert rv.status_code == 201
		assert self.pet_1.name in str(rv.data)
		rv = self.client.post('/pets', data=json.dumps(self.pet_2.serialize()), content_type='application/json')
		assert rv.status_code == 201
		assert self.pet_2.name in str(rv.data)
		rv = self.client.post('/pets', data=json.dumps(self.pet_3.serialize()), content_type='application/json')
		assert rv.status_code == 201
		assert self.pet_3.name in str(rv.data)

		rv = self.client.get('/search_pets', query_string={'breed': 'chihuahua'})
		assert rv.status_code == 200
		assert self.pet_1.name not in str(rv.data)
		assert self.pet_2.name in str(rv.data)
		assert self.pet_3.name not in str(rv.data)

		rv = self.client.get('/search_pets', query_string={'type': 'dog', 'found_location_x': 12, 'found_location_y': 11})
		assert rv.status_code == 200
		assert self.pet_1.name not in str(rv.data)
		assert self.pet_2.name in str(rv.data)
		assert self.pet_3.name not in str(rv.data)

	def test_can_search_available_shelters(self):
		rv = self.client.post('/cities', data=json.dumps(self.city_1.serialize()), content_type='application/json')
		assert rv.status_code == 201
		assert self.city_1.name in str(rv.data)
		rv = self.client.post('/cities/1/shelters', data=json.dumps(self.shelter_1.serialize()), content_type='application/json')
		assert rv.status_code == 201
		assert self.shelter_1.name in str(rv.data)
		rv = self.client.post('/cities/1/shelters', data=json.dumps(self.shelter_2.serialize()), content_type='application/json')
		assert rv.status_code == 201
		assert self.shelter_2.name in str(rv.data)
		rv = self.client.post('/cities/1/shelters', data=json.dumps(self.shelter_3.serialize()), content_type='application/json')
		assert rv.status_code == 201
		assert self.shelter_3.name in str(rv.data)
		rv = self.client.post('/shelters/1/pets', data=json.dumps(self.pet_1.serialize()), content_type='application/json')
		assert rv.status_code == 201
		assert self.pet_1.name in str(rv.data)
		rv = self.client.post('/shelters/2/pets', data=json.dumps(self.pet_2.serialize()), content_type='application/json')
		assert rv.status_code == 201
		assert self.pet_2.name in str(rv.data)
		rv = self.client.post('/shelters/2/pets', data=json.dumps(self.pet_3.serialize()), content_type='application/json')
		assert rv.status_code == 201
		assert self.pet_3.name in str(rv.data)

		rv = self.client.get('/search_available_shelters', query_string={})
		assert self.shelter_1.name in str(rv.data)
		assert self.shelter_2.name not in str(rv.data)
		
		rv = self.client.get('/search_available_shelters', query_string={'found_location_x': 150, 'found_location_y': 15})
		assert self.shelter_1.name not in str(rv.data)
		assert self.shelter_2.name not in str(rv.data)
		# assert self.shelter_3.name in str(rv.data)

		rv = self.client.get('/search_available_shelters', query_string={'found_location_x': 50, 'found_location_y': 50})
		assert self.shelter_1.name not in str(rv.data)
		assert self.shelter_2.name not in str(rv.data)

	def test_user_registration(self):
		res = self.client.post('/auth/register', data=json.dumps(self.user_data), content_type='application/json')
		result = json.loads(res.data.decode())
		assert result['message'] == 'You registered successfully. Please login.'
		assert res.status_code == 201

	def test_already_registered_user(self):
		res = self.client.post('/auth/register', data=json.dumps(self.user_data), content_type='application/json')
		assert res.status_code == 201
		second_res = self.client.post('/auth/register', data=json.dumps(self.user_data), content_type='application/json')
		assert second_res.status_code == 202
		result = json.loads(second_res.data.decode())
		assert result['message'] == 'User already exists. Please login.'

	def test_user_login(self):
		res = self.client.post('/auth/register', data=json.dumps(self.user_data), content_type='application/json')
		assert res.status_code == 201
		login_res = self.client.post('/auth/login', data=json.dumps(self.user_data), content_type='application/json')

		result = json.loads(login_res.data.decode())
		assert result['message'] == 'You logged in successfully.'
		assert login_res.status_code == 200
		assert result['access_token']

	# def test_non_registered_user_login(self):
	# 	res = self.client.post('/auth/login', data=json.dumps(self.not_user_data), content_type='application/json')
	# 	result = json.loads(res.data.decode())
	# 	assert res.status_code == 401
	# 	assert result['message'] == 'Invalid email or password. Please try again.'













if __name__ == '__main__':
	unittest.main()