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
            self.__load()

    # Load instance from db
    def __load(self):

        if not self.user_id:

            raise Exception

        db_user = self.__db_user()
        self.created = db_user.created
        self.last_login = db_user.last_login
        self.username = db_user.username
        self.password = db_user.password
        self.email = db_user.email
        self.active = db_user.active
        self.display_name = db_user.display_name

    def save(self):

        from dbModel import DbUser
        from sqlalchemy import func
        from db import csdb
        session = csdb.session

        db_user = self.__db_user()
        db_user.username = self.username
        db_user.password = self.password
        db_user.email = self.email
        db_user.active = self.active
        db_user.display_name = self.display_name

        # Add if it does not exist already in db
        if not self.user_id:
            session.add(db_user)

        session.commit()

    def set_encrypted_password(self, password):

        import db
        session = db.csdb.session
        self.password = session.query('encrypted_password').from_statement("SELECT SHA1(:password) AS encrypted_password").params(password = password).one()[0]

    def activate(self):

        import db
        session = db.csdb.session
        db_user = self.__db_user()
        db_user.active = 1
        self.active = 1
        session.commit()

    def update_roles(self, role_ids):

        import db
        from dbModel import DbRole
        session = db.csdb.session
        db_user = self.__db_user()

        db_user.roles = []
        for role_id in role_ids:
            query = session.query(DbRole).filter(DbRole.role_id == role_id)
            if query.count() == 1:
                db_user.roles.append(query.one())
        session.commit()

    def role_ids(self):

        db_user = self.__db_user()
        ids = []
        for role in db_user.roles:
           ids.append(role.role_id)

        return ids

    def role_names(self):

        db_user = self.__db_user()
        names = []
        for role in db_user.roles:
           names.append(role.names)

        return names

    def privilege_ids(self):

        db_user = self.__db_user()
        privilege_ids = []
        for role in db_user.roles:

            # Administrator can do everything
            if role.role_id == 1:

                import db
                from dbModel import DbPrivilege
                session = db.csdb.session
                for privilege in session.query(DbPrivilege):

                    privilege_ids.append(privilege.privilege_id)
                
            else:

                for privilege in role.privileges:

                    privilege_ids.append(privilege.privilege_id)

        return privilege_ids

    def is_administrator(self):

        return 1 in self.role_ids()

    def is_moderator(self):

        return 2 in self.role_ids()

    def __db_user(self):

        import db
        from dbModel import DbUser
        from sqlalchemy import func
        session = db.csdb.session
        if self.user_id:
            db_user = session.query(DbUser).filter(DbUser.user_id == self.user_id).one()
        else:
            db_user = DbUser()
            db_user.created = func.now()
        return db_user

# Get User instance from username and password
# @param string username Username
# @param string password Passowrd
# @return User
def getInstanceFromUsernamePassword(username, password):

    from dbModel import DbUser
    from sqlalchemy import func
    import db
    session = db.csdb.session
    db_user = session.query(DbUser).filter(DbUser.username == username).filter(DbUser.password == func.sha1(password)).filter(DbUser.active == 1).one()
    return User(db_user.user_id)

# Get User instance from username
# @param string username Username
# @return User
def getInstanceFromUsername(username):

    from dbModel import DbUser
    import db
    session = db.csdb.session
    db_user = session.query(DbUser).filter(DbUser.username == username).one()
    return User(db_user.user_id)

# Check to see if username exists
# @param string username Username to check
# @param integer exclude_user_id (Optional) Exclude user id (used for checking existing users)
def usernameExists(username, exclude_user_id = None):

    from dbModel import DbUser
    from sqlalchemy import func
    import db
    session = db.csdb.session
    query = session.query(DbUser).filter(DbUser.username == username)
    if exclude_user_id:
        query.filter(DbUser.user_id != exclude_user_id)
    return query.count() != 0

# Get data
# @return array
def get_data(exclude_administrators = True):

    from dbModel import DbUser
    import db
    session = db.csdb.session
    users = []
    for user in session.query(DbUser).order_by(DbUser.active.desc()).order_by(DbUser.display_name):
        is_administrator = False
        roles = []
        for role in user.roles:
            roles.append(role.name)
            if role.role_id == 1:
                is_administrator = True
        if exclude_administrators and is_administrator:
            continue
        users.append({
            'user_id': user.user_id,
            'username': user.username,
            'display_name': user.display_name,
            'created': user.created,
            'last_login': user.last_login,
            'roles': ', '.join(roles),
            'active': user.active
        })
    return users
