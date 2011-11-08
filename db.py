from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

_engine = None
_session = None

def engine():

    global _engine
    if _engine == None:
        _engine = create_engine('mysql://cs_guest:csblubber@localhost/climbspotter_dev')
    return _engine

def session():

    global _session, engine
    if _session == None:

        engine = engine()
        Session = sessionmaker(bind=engine)
        _session = Session()

    return _session
