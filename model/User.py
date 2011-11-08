# User Class
class User(object):

    user_id = None
    created = None
    last_login = None
    username = None
    password = None
    email = None
    active = 0
    display_name = None

    # Constructor
    # @param integer user_id (Optional) User id
    def __init__(self, user_id = None):

        if user_id:

            self.user_id = user_id
            self._load()

    # Load instance from db
    def _load(self):

        if not self.user_id:

            raise Exception

        from dbModel import DbUser
        import db
        session = db.session()
        dbUser = session.query(DbUser).filter(DbUser.user_id == self.user_id).one()
        self.created = dbUser.created
        self.last_login = dbUser.last_login
        self.username = dbUser.username
        self.password = dbUser.password
        self.email = dbUser.email
        self.active = dbUser.active
        self.display_name = dbUser.display_name

# Get User instance from username and password
# @param string username Username
# @param string password Passowrd
# @return User
def getInstanceFromUsernamePassword(username, password):

    from dbModel import DbUser
    from sqlalchemy import func
    import db
    session = db.session()
    dbUser = session.query(DbUser).filter(DbUser.username == username).filter(DbUser.password == func.sha1(password)).one()
    return User(dbUser.user_id)

# Get User instance from username
# @param string username Username
# @return User
def getInstanceFromUsername(username):

    from dbModel import DbUser
    from sqlalchemy import func
    import db
    session = db.session()
    dbUser = session.query(DbUser).filter(DbUser.username == username).one()
    return User(dbUser.user_id)

# Get data
# @return array
def getData():

    from dbModel import DbUser
    import db
    session = db.session()
    users = []
    for user in session.query(DbUser).order_by(DbUser.username):
        users.append({
            'username': user.username,
            'display_name': user.display_name,
            'created': user.created,
            'last_login': user.last_login,
            'roles': '',
            'active': user.active
        })
    return users