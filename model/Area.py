
class Area(object):

    area_id = None
    name = None
    created = None

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

    def save(self):

        from dbModel import DbArea
        from sqlalchemy import func
        import db
        session = db.session()

        db_area = self.__db_area()
        db_area.name = self.name
        db_area.created = self.created

        # Add if it does not exist already in db
        if not self.area_id:
            session.add(db_area)

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

def search(str):

    from dbModel import DbArea

    import db
    session = db.session()
    areas = []
    for area in session.query(DbArea).filter(DbArea.name.like("{0}%".format(str))).order_by(DbArea.name):
        areas.append({
            'area_id': area.area_id,
            'name': area.name,
        })
    return areas
