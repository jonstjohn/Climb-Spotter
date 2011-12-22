import csv, sys

sys.path.append('/home/jonstjohn/climbspotter/dev/code')

from model import Area
# Book,Region,Wall,Type,Latitude (Coord Y),Longitude (Coord X),Count
path = '/home/jonstjohn/climbspotter/dev/data/areas.csv'
book = ''
region = ''
wall = ''
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
        if tp == 'Book Point':
            name = book
        elif tp == 'Region Point':
            name = region
        elif tp == 'Wall Point':
             name = wall

        if len(tp):
            print("{0} - {1} - {2} - {3} - {4} - {5}".format(tp, book, region, wall, latitude, longitude))

            # Insert into area
