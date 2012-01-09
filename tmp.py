from dbModel import DbArea, DbRoute
from model import Area, Route
import db, sys

import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

session = db.session()

print("Areas for Leave it to Jesus")
db_route = session.query(DbRoute).filter(DbRoute.route_id == 1).one()
for area in db_route.area.ancestors:

    print(area.name)

print("Routes for Kaymoor")
db_area = session.query(DbArea).filter(DbArea.area_id == 4).one()
for route in db_area.routes:

    print(route.name)

sys.exit(1)




db_route = session.query(DbRoute).filter(DbRoute.route_id == 1).one()
for area in db_route.area.ancestors:

    print(area.name)



sys.exit(1)
db_area = session.query(DbArea).filter(DbArea.area_id == 4).one()
print("Ancestors {0}".format(len(db_area.ancestors)))

for area in db_area.ancestors:

    print(area.name)

print("Descendents {0}".format(len(db_area.descendents)))
for area in db_area.descendents:

    print(area.name)
#print(db_area.descendents[0].name)

#area = Area.Area()
#area.name = 'Domino Point'
#area.parent_id = 1
#area.save()
