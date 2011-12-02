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
