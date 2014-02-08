import csv, sys

sys.path.append('/home/jonstjohn/climbspotter/dev/code')

from model import Area
from dbModel import DbArea
import db

# Book,Region,Wall,Type,Latitude (Coord Y),Longitude (Coord X),Count
path = '/home/jonstjohn/climbspotter/dev/data/areas.csv'
book = ''
region = ''
wall = ''

session = db.csdb.session

with open(path, 'rb') as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row[0]):
            book = row[0].strip()
            region = ''
            wall = ''
        region = row[1].strip() if len(row[1]) else region
        wall =row[2].strip() if len(row[2]) else wall
        tp = row[3].strip()
        latitude = row[4].strip()
        longitude = row[5].strip()

        name = ''
        parent = None
        if tp == 'Book Point':
            name = book
        elif tp == 'Region Point':
            name = region
            parent = book
        elif tp == 'Wall Point':
             name = wall
             parent = region

        if len(tp):
            print("{0} - {1} - {2} - {3} - {4} - {5}".format(tp, book, region, wall, latitude, longitude))

            # Check to see if name exists
            #if len(Area.search(name, exact = True)) != 0:
            #    print(" **** SKIPPING {0} *****".format(name))
            #    continue

            area = Area.Area()
            area.name = name
            area.latitude = latitude
            area.longitude = longitude

            # If it does not exist, look up parent
            if parent:
                parents = Area.search(parent, exact = True) 
                if len(parents) == 1:
                    area.parent_id = parents[0]['area_id']
                

            # Insert into area
            area.save()
