
class Area(object):

    area_id = None
    name = None
    created = None
    parent_id = None
    latitude = None
    longitude = None

    # Constructor
    # @param integer area_id (Optional) Area work id
    def __init__(self, area_id = None):

        if area_id:

            self.area_id = area_id
            self.__load()

    # Load instance from db
    def __load(self):

        if not self.area_id:

            raise Exception

        db_area = self.__db_area()
        self.created = db_area.created
        self.name = db_area.name
        self.latitude = db_area.latitude
        self.longitude = db_area.longitude

    def save(self):

        from dbModel import DbArea
        from sqlalchemy import func
        import db
        session = db.session()

        db_area = self.__db_area()
        db_area.name = self.name
        db_area.latitude = self.latitude
        db_area.longitude = self.longitude

        # Add if it does not exist already in db
        if not self.area_id:
            session.add(db_area)

        # Create associations - add parent relationship plus any additional parents of parent
        if self.parent_id:

            # Select all ancestors of parent id, since this will also be an ancestor of area
            parent = session.query(DbArea).filter(DbArea.area_id == self.parent_id).one()
            for a in parent.ancestors:
                db_area.ancestors.append(a)

        # insert self-referential record
        db_area.ancestors.append(db_area)


        # Consider whether or not this area was moved - delete previous associations and re-create all others
        session.commit()

    def __db_area(self):

        import db
        from sqlalchemy import func
        from dbModel import DbArea
        session = db.session()
        if self.area_id:
            db_area = session.query(DbArea).filter(DbArea.area_id == self.area_id).one()
        else:
            db_area = DbArea()
            db_area.created = func.now()

        return db_area

def search(str, exact = False, parent_id = None):

    from dbModel import DbArea

    import db
    session = db.session()
    areas = []

    srch = str
    if not exact:
        srch = "{0}%".format(srch)

    query = session.query(DbArea).filter(DbArea.name.like(srch)).order_by(DbArea.name)

    for area in query:
        areas.append({
            'area_id': area.area_id,
            'name': area.name,
        })
    return areas
