import json
import unittest
from hello import create_app, db, City, Shelter, Pet

class HelloTestCase(unittest.TestCase):

	def setUp(self):
		self.app = create_app(config_name='testing')
		self.app.testing = True
		self.client = self.app.test_client()
		self.city_1 = {'name': 'Seattle'}
		self.city_2 = {'name': 'Boston'}

		with self.app.app_context():
			db.drop_all()
			db.create_all()

	def tearDown(self):
		with self.app.app_context():
			db.session.remove()
			db.drop_all()

	def addOneCity(self):
		city = City('Seattle')
		db.session.add(city)
		db.session.commit()

	def testRoot(self):
		rv = self.client.get('/')
		assert rv.status_code == 200
		assert 'Welcome to Exceptional!' in str(rv.data)

	def test_can_create_city(self):
		rv = self.client.post('/cities', data=json.dumps(self.city_1), content_type='application/json')
		assert rv.status_code == 201
		assert self.city_1['name'] in str(rv.data)

	def test_can_query_all_cities(self):
		rv = self.client.post('/cities', data=json.dumps(self.city_1), content_type='application/json')
		assert rv.status_code == 201
		assert self.city_1['name'] in str(rv.data)
		rv = self.client.get('/cities')
		assert rv.status_code == 200
		assert self.city_1['name'] in str(rv.data)

	def test_can_query_city_by_id(self):
		rv = self.client.post('/cities', data=json.dumps(self.city_1), content_type='application/json')
		assert rv.status_code == 201
		assert self.city_1['name'] in str(rv.data)
		id = json.loads(rv.data.decode('utf-8').replace("'", "\""))['id']
		rv = self.client.get('/cities/{}'.format(id))
		assert rv.status_code == 200
		assert self.city_1['name'] in str(rv.data)

	def test_can_edit_city_by_id(self):
		rv = self.client.post('/cities', data=json.dumps(self.city_1), content_type='application/json')
		assert rv.status_code == 201
		assert self.city_1['name'] in str(rv.data)
		id = json.loads(rv.data.decode('utf-8').replace("'", "\""))['id']
		rv = self.client.put('/cities/{}'.format(id), data=json.dumps(self.city_2), content_type='application/json')
		assert rv.status_code == 200
		assert self.city_2['name'] in str(rv.data)
		rv = self.client.get('/cities/{}'.format(id))
		assert self.city_2['name'] in str(rv.data)

	def test_can_delete_city_by_id(self):
		rv = self.client.post('/cities', data=json.dumps(self.city_1), content_type='application/json')
		assert rv.status_code == 201
		assert self.city_1['name'] in str(rv.data)
		id = json.loads(rv.data.decode('utf-8').replace("'", "\""))['id']
		rv = self.client.delete('/cities/{}'.format(id))
		assert rv.status_code == 200
		rv = self.client.get('/cities/{}'.format(id))
		assert rv.status_code == 404

if __name__ == '__main__':
	unittest.main()