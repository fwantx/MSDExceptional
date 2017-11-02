from hello import db
from hello import Shelter
from hello import City

# c1 = City(name='Seattle')
# c2 = City(name='Austin')
# c3 = City(name='New York')
#
# s1 = Shelter(name='Northgate Pet Shelter', city_id=1, location_x=0, location_y=0, kennel_num=2)
# s2 = Shelter(name='Westlake Animal Shelter', city_id=1, location_x=10, location_y=0, kennel_num=5)
# s3 = Shelter(name='Texas Dog Center', city_id=2, location_x=20, location_y=10, kennel_num=10)
# s4 = Shelter(name='Big Apple Animal Center', city_id=3, location_x=30, location_y=10, kennel_num=10)
#
# db.session.add(c1)
# db.session.add(c2)
# db.session.add(c3)
# db.session.add(s1)
# db.session.add(s2)
# db.session.add(s3)
# db.session.add(s4)

db.session.commit()