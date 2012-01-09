class Route(object):

    route_id = None
    area_id = None
    name = None
    created = None

    # Constructor
    # @param integer route_id (Optional) Route work id
    def __init__(self, route_id = None):

        if route_id:

            self.route_id = route_id
            self.__load()

    # Load instance from db
    def __load(self):

        if not self.route_id:

            raise Exception

        db_route = self.__db_route()
        self.created = db_route.created
        self.name = db_route.name
        self.area_id = db_route.area_id

    def save(self):

        from dbModel import DbRoute
        from sqlalchemy import func
        import db
        session = db.session()

        db_route = self.__db_route()
        db_route.name = self.name
        db_route.area_id = self.area_id

        # Add if it does not exist already in db
        if not self.route_id:
            session.add(db_route)

        session.commit()

    def __db_route(self):

        import db
        from sqlalchemy import func
        from dbModel import DbRoute
        session = db.session()
        if self.route_id:
            db_route = session.query(DbRoute).filter(DbRoute.route_id == self.route_id).one()
        else:
            db_route = DbRoute()
            db_route.created = func.now()
        return db_route

def search(str, area_id = None):

    from dbModel import DbRoute

    import db
    session = db.session()
    routes = []

    #SELECT route.route_id, route.name
    #FROM area INNER JOIN area_relationship ON area.area_id = area_relationship.ancestor
    #INNER JOIN route ON route.area_id = area_relationship.descendent
    #WHERE area.area_id = 1

    query = session.query(DbRoute).filter(DbRoute.name.like("{0}%".format(str))).order_by(DbRoute.name);
    if area_id:
        query = query.filter(DbRoute.area_id == area_id)
    for route in query:
        routes.append({
            'route_id': route.route_id,
            'name': route.name,
        })
    return routes
