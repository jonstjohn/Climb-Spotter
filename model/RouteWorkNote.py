# Route work class
class RouteWorkNote(object):

    route_work_note_id = None
    route_work_id = None
    user_id = None
    note = None
    created = None

    # Constructor
    # @param integer route_work_note_id (Optional) Route work id
    def __init__(self, route_work_note_id = None):

        if route_work_note_id:

            self.route_work_note_id = route_work_note_id
            self.__load()

    # Load instance from db
    def __load(self):

        if not self.route_work_note_id:

            raise Exception

        db_route_work_note = self.__db_route_work_note()
        self.created = db_route_work_note.created
        self.route_work_id = db_route_work_note.route_work_id
        self.user_id = db_route_work_note.user_id
        self.note = db_route_work.note
        self.created = db_route_work_note.created

    def save(self):

        from dbModel import DbRouteWorkNote
        from sqlalchemy import func
        import db
        session = db.csdb.session

        db_route_work_note = self.__db_route_work_note()
        db_route_work_note.route_work_id = self.route_work_id
        db_route_work_note.user_id = self.user_id
        db_route_work_note.note = self.note
        db_route_work_note.created = self.created

        # Add if it does not exist already in db
        if not self.route_work_note_id:
            session.add(db_route_work_note)

        session.commit()

    def __db_route_work_note(self):

        import db
        from sqlalchemy import func
        from dbModel import DbRouteWorkNote
        session = db.csdb.session
        if self.route_work_note_id:
            db_route_work_note = session.query(DbRouteWorkNote).filter(DbRouteWorkNote.route_work_note_id == self.route_work_note_id).one()
        else:
            db_route_work_note = DbRouteWorkNote()
            db_route_work_note.created = func.now()
        return db_route_work_note
