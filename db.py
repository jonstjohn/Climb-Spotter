from flask.ext.sqlalchemy import SQLAlchemy
import CsConfiguration

c = CsConfiguration.CsConfiguration()
username = c.settings['database']['username']
password = c.settings['database']['password']
host = c.settings['database']['host']
database = c.settings['database']['database']
dbtype = c.settings['database']['type']

db_uri = "{}://{}:{}@{}/{}".format(dbtype, username, password, host, database)
csdb = None

def init(app):
    # Initialize db
    global csdb
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    csdb = SQLAlchemy(app)
    return csdb
