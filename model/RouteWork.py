# Route work class
class RouteWork(object):

    route_work_id = None
    user_id = None
    route_id = None
    route_work_id = None
    who = None
    work_date = None
    bolts_placed = None
    anchor_replaced = None
    new_anchor = None
    created = None
    info = None

    # Constructor
    # @param integer route_work_id (Optional) Route work id
    def __init__(self, route_work_id = None):

        if route_work_id:

            self.route_work_id = route_work_id
            self.__load()

    # Load instance from db
    def __load(self):

        if not self.route_work_id:

            raise Exception

        db_route_work = self.__db_route_work()
        self.created = db_route_work.created
        self.route_id = db_route_work.route_id
        self.user_id = db_route_work.user_id
        self.who = db_route_work.who
        self.work_date = db_route_work.work_date
        self.bolts_placed = db_route_work.bolts_placed
        self.anchor_replaced = db_route_work.anchor_replaced
        self.new_anchor = db_route_work.new_anchor
        self.created = db_route_work.created
        self.info = db_route_work.info

    def save(self):

        from dbModel import DbRouteWork
        from sqlalchemy import func
        import db
        session = db.csdb.session

        db_route_work = self.__db_route_work()
        db_route_work.route_id = self.route_id
        db_route_work.user_id = self.user_id
        db_route_work.who = self.who
        db_route_work.work_date = self.work_date
        db_route_work.bolts_placed = self.bolts_placed
        db_route_work.anchor_replaced = self.anchor_replaced
        db_route_work.new_anchor = self.new_anchor
        db_route_work.created = self.created
        db_route_work.info = self.info

        # Add if it does not exist already in db
        if not self.route_work_id:
            session.add(db_route_work)

        session.commit()
        self.route_work_id = db_route_work.route_work_id

    def get_route_name(self):
   
        rw = self.__db_route_work()
        return rw.route.name

    def get_area_name(self):

        rw = self.__db_route_work()
        return rw.route.area.name

    def get_area_id(self):

        rw = self.__db_route_work()
        return rw.route.area.area_id

    def get_note_data(self):

        data = []
        d = self.__db_route_work()
        for note in d.notes:

            data.append(
                {'route_work_note_id':  note.route_work_note_id, 'note': note.note,
                    'user': note.user.display_name, 'created': note.created}
            )

        return data

    # Add note to route work
    def add_note(self, note, user_id):

        import db
        from dbModel import DbRouteWorkNote
        from sqlalchemy import func
        session = db.csdb.session
        db_note = DbRouteWorkNote()
        db_note.created = func.now()
        db_note.user_id = user_id
        db_note.route_work_id = self.route_work_id
        db_note.note = note
        session.add(db_note)
        session.commit()

    def delete(self):

        import db
        session = db.csdb.session
        rw = self.__db_route_work()
        session.delete(rw)
        session.commit()

    def __db_route_work(self):

        import db
        from sqlalchemy import func
        from dbModel import DbRouteWork
        session = db.csdb.session
        if self.route_work_id:
            db_route_work = session.query(DbRouteWork).filter(DbRouteWork.route_work_id == self.route_work_id).one()
        else:
            db_route_work = DbRouteWork()
            db_route_work.created = func.now()
        return db_route_work

# Get data
# @return array
def get_data(exclude_administrators = True):

    from dbModel import DbRouteWork
    import db, time
    session = db.csdb.session
    route_works = []
    for route_work in session.query(DbRouteWork).order_by(DbRouteWork.work_date.desc()):
        work_date = None
        if route_work.work_date:
            work_date_struct = time.strptime(str(route_work.work_date), '%Y-%m-%d %H:%M:%S')
            work_date = time.strftime('%m/%d/%Y', work_date_struct)
        route_works.append({
            'route_work_id': route_work.route_work_id,
            'route_name': route_work.route.name,
            'area_name': route_work.route.area.name,
            'work_date': work_date,
            'who': route_work.who,
            'bolts_placed': route_work.bolts_placed,
            'anchor_replaced': route_work.anchor_replaced,
            'new_anchor': route_work.new_anchor
        })
    return route_works
