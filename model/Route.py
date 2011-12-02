def search(str, area_id = None):

    from dbModel import DbRoute

    import db
    session = db.session()
    routes = []

    query = session.query(DbRoute).filter(DbRoute.name.like("{0}%".format(str))).order_by(DbRoute.name);
    if area_id:
        query = query.filter(DbRoute.area_id == area_id)
    for route in query:
        routes.append({
            'route_id': route.route_id,
            'name': route.name,
        })
    return routes
