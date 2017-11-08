import unittest
from hello import app, db, City, Shelter, Pet

class HelloTestCase(unittest.TestCase):

	def setUp(self):
		app.testing = True
		self.app = app.test_client()

	def tearDown(self):
		pass

	def testRoot(self):
		rv = self.app.get('/')
		assert rv.status_code == 200
		assert rv.data == b'Welcome to Exceptional!'


if __name__ == '__main__':
	unittest.main()