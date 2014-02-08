import csv, sys

sys.path.append('/home/jonstjohn/climbspotter/dev/code')

from model import Area, Route
from dbModel import DbArea
import db

f = open('/home/jonstjohn/climbspotter/dev/data/route.txt', 'r')

import re

area_lookup = {}
route_pages = {}
max_page = 1

session = db.csdb.session

# Parse file
p = re.compile('(.*)\.\.+([0-9]*)')
for line in f:

    #print line,
    m = p.match(line)

    name = m.group(1).strip()
    name = name.rstrip('.')
    page = m.group(2).strip()
    page = int(page.lstrip('.'))
    if page > max_page:
        max_page = page

    if not page in route_pages:
        route_pages[page] = []

    areas = Area.search(name, exact = True)
    if len(areas) == 1:
        area_lookup[page] = (areas[0]['area_id'], name)
    elif len(areas) > 1:
        print(" **** {0} areas found for '{1}' ****".format(len(areas), name))
    else:
        route_pages[page].append(name)

    #print("  {0}-{1}".format(name, page))

area_id = None
for page in range(1,max_page+1):

    print("Page {0}".format(page))
    if page in area_lookup:
        print ("  AREA - {0} ({1})".format(area_lookup[page][1], area_lookup[page][0]))
        area_id = area_lookup[page][0]
    if page in route_pages:
        for route in route_pages[page]:
            print("  {0} ({1})".format(route, area_id))
            r = Route.Route()
            r.name = route
            r.area_id = area_id
            r.save()

sys.exit(1)

# Loop over all our areas, try to find in file, start with shortest path length
for area in session.query(DbArea).order_by(DbArea.area_id):

    print(area.name)
    if area.name in routes:
        print("-".join(routes[area.name]))
    else:
        print(" ***** NOT FOUND ****** ")
    
#    areas = Area.search(name, exact = True)
#    if len(areas) != 0:
#        area_lookup[areas[0]['area_id']] = page
#        print("  ** Appears to be area **")
#        if len(areas) > 1:
#            print(" XXXXX           MORE THAN ONE MATCH             XXXX")

print("AREAS")

for name, page in area_lookup.iteritems():

    print("{0} - {1}".format(name, page))
