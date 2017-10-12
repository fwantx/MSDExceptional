from hello import db
from hello import Shelter
s1 = Shelter(name='SeattleShelter', location_x=0, location_y=0, kennel_num=2)
s2 = Shelter(name='BellevueShelter', location_x=10, location_y=0, kennel_num=5)

db.session.add(s1)
db.session.add(s2)

db.session.commit()