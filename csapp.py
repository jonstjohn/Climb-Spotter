from flask import Flask
from flask import render_template
from flask import request, session
from flask import abort, redirect, url_for, flash

from functools import wraps

import sqlalchemy
import json
import db

app = Flask(__name__)

# set the secret key.  keep this really secret:
app.secret_key = 'ADDefA221 -9981 Bdd%kkkll'

# Convert sql date to form date
def __sql_to_form(sql):

    import time
    struct_struct = time.strptime(str(sql), '%Y-%m-%d %H:%M:%S')
    return time.strftime('%m/%d/%Y', struct_struct)

def __form_to_sql(form):

    import time
    struct_struct = time.strptime(str(form), '%m/%d/%Y')
    return time.strftime('%Y-%m-%d 00:00:00', struct_struct)

def __authenticated_user():

    from model import User
    return User.User(session['user_id'])

# Check privelege, used as decorator
def check_priv(privilege_id):

    def check_priv_decorator(f):
        
        @wraps(f)
        
        def decorated_function(*args, **kwargs):

            # Redirect if not logged in
            if not 'user_id' in session or not session['user_id']:

                return redirect(url_for('index', next=request.url))

            else:

                # Check for valid role
                from model import User
                user = User.User(session['user_id'])
                if not privilege_id in user.privilege_ids():

                    return redirect(url_for('access_denied'))

            # If logged in and privileged, display page
            return f(*args, **kwargs)

        return decorated_function

    return check_priv_decorator

# Check for valid login, used as decorator
def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not 'user_id' in session or not session['user_id']:
            return redirect(url_for('index', next=request.url))
        return f(*args, **kwargs)

    return decorated_function

#@app.context_processor
#def inject_privileges():
#
#    if 'user_id' in session:
#        from model import User
#        user = User.User(session['user_id'])
#        return dict(privilege_ids = user.privilege_ids())

@app.context_processor
def inject_menu():

    menu_items = []
    if 'user_id' in session:

        from model import User
        user = User.User(session['user_id'])
        privilege_ids = user.privilege_ids()
        if 1 in privilege_ids:
            item = {'label': 'Manage Users', 'url': url_for('user_manage'), 'active': False}
            if request.path.find('/u/user') == 0:
                item['active'] = True
            menu_items.append(item)
        if 3 in privilege_ids:
            item = {'label': 'View Route Work', 'url': url_for('route_list'), 'active': False}
            if request.path.find('/u/route-work/list') == 0:
                item['active'] = True
            menu_items.append(item)
        if 2 in privilege_ids:
            item = {'label': 'Submit Route Work', 'url': url_for('route_work_form'), 'active': False}
            if request.path.find('/u/route-work/form') == 0:
                item['active'] = True
            menu_items.append(item)
        if 1 in privilege_ids:
            item = {'label': 'Invite Users', 'url': url_for('invite_form'), 'active': False}
            if request.path.find('/u/invite') == 0:
                item['active'] = True
            menu_items.append(item) 
    return dict(menu_items = menu_items)

@app.route('/')
def index(post_id = None, slug = None):

    return render_template('index.html')

@app.route('/access-denied')
def access_denied():

    return render_template('denied.html')


@app.route('/register')
def register():

    return render_template('register.html')

@app.route('/contact')
def contact():
    
    return render_template('contact.html')

@app.route('/contact-submit', methods=['POST'])
def contact_submit():

    import smtplib
    import string
 
    subject = "Contact Form from ClimbSpotter.com"
    to = "jonstjohn@gmail.com"
    frm = request.form['email']
    text = request.form['message']
    body = string.join((
        "From: admin@climbspotter.com", # % frm,
        "Reply-to: %s" % frm,
        "To: %s" % to,
        "Subject: %s" % subject ,
        "",
        text
    ), "\r\n")
    server = smtplib.SMTP('localhost')
    server.sendmail(frm, [to], body)
    server.quit()

    return redirect(url_for('contact_done'))

@app.route('/contact-done')
def contact_done():

    return render_template('contact_done.html')

@app.route('/register-submit', methods=['POST'])
def register_submit():

    from model import User

    errors = []
    # Validate data
    # Check for required fields
    labels = {'username': 'Username', 'password': 'Password',
        'password2': 'Re-type Password', 'email': 'E-mail',
        'email2': 'Re-type Email', 'display_name': 'Display Name'}
    for el in ['username', 'password', 'password2', 'email', 'email2', 'display_name']:
        if el not in request.form or len(request.form[el]) == 0:
            errors.append("'{0}' is a required field.".format(labels[el]))

    # Make sure username is not currently used
    if User.usernameExists(request.form['username']):
        errors.append("The username '{username}' already exists in our system. Please choose a different one.".format(username = request.form['username']))

    # Compared passwords and emails
    if request.form['password'] != request.form['password2']:
        errors.append('Passwords must match.')
    if request.form['email'] != request.form['email2']:
        errors.append('E-mail addresses must match.')

    # No spaces in username or password
    if ' ' in request.form['username']:
        errors.append('Username may not contain spaces')
    if len(request.form['username']) not in range(4, 31):
        errors.append('Username must be 4-30 characters long.')
    if len(request.form['password']) not in range(6, 21):
        errors.append('Password must be 6-20 characters long.')

    # If errors, display form again
    if len(errors) != 0:

        return render_template(
            'register.html', error = "<br/>\n".join(errors),
            username = request.form['username'],
            password = request.form['password'],
            password2 = request.form['password2'],
            email = request.form['email'],
            email2 = request.form['email2'],
            display_name = request.form['display_name']
        )

    # If no errors, save user as not active and redirect to awaiting approval page
    user = User.User()
    user.username = request.form['username']
    user.set_encrypted_password(request.form['password'])
    user.email = request.form['email']
    user.display_name = request.form['display_name']
    user.save()

    import smtplib
    import string

    subject = "New Registration on ClimbSpotter.com"
    to = "jonstjohn@gmail.com"
    frm = request.form['email']
    text = "A new registration has been received for '{0}' ({1})".format(request.form['display_name'], request.form['username'])
    body = string.join((
        "From: admin@climbspotter.com", # % frm,
        "Reply-to: %s" % frm,
        "To: %s" % to,
        "Subject: %s" % subject ,
        "",
        text
    ), "\r\n")
    server = smtplib.SMTP('localhost')
    server.sendmail(frm, [to], body)
    server.quit()

    
    return redirect(url_for('register_done'))


@app.route('/send')
def send():

    import smtplib
    from email.mime.text import MIMEText

    msg = MIMEText('Test')
    msg['Subject'] = 'Test Send'
    msg['From'] = 'jon@drivecurrent.com'
    msg['To'] = 'jonstjohn@gmail.com'
    s = smtplib.SMTP('localhost')
    s.sendmail('jon@drivecurrent.com', ['jonstjohn@gmail.com'], msg.as_string())
    return 'test'

@app.route('/register-done')
def register_done():

    return render_template('registerDone.html')
    

@app.route('/login-submit', methods=['POST'])
def login_submit():
    from model import User

    try:
        user = User.getInstanceFromUsernamePassword(request.form['username'], request.form['password'])
        session['user_id'] = user.user_id

        role_ids = user.role_ids()
        url = url_for('route_list')
        if 1 in role_ids or 2 in role_ids:
            url = url_for('user_manage')
        return redirect(url)

    except sqlalchemy.orm.exc.NoResultFound:
        flash('Invalid username and/or password')
        return redirect(url_for('index'))

@app.route('/u')
@check_priv(1)
def user():

    from model import User
    return render_template('user/index.html', users = User.get_data())

@app.route('/u/user')
@login_required
@check_priv(1)
def user_manage():

    from model import User

    import db
    from dbModel import DbInvite
    session = db.session()
    return render_template('user/index.html', users = User.get_data(), invites = session.query(DbInvite).order_by(DbInvite.email))

@app.route('/u/invite/form')
@login_required
@check_priv(1)
def invite_form():

    return render_template('invite/form.html')

@app.route('/u/invite/submit', methods = ['POST'])
@login_required
@check_priv(1)
def invite_submit():

    import smtplib
    import string

    subject = "ClimbSpotter.com Invite"
    to = request.form['email']
    text = "You have been invited to ClimbSpotter.com, an anchor replacement and bolt tracking system for the climbing community.\n\n"
    text += "You are receiving this email because a moderator has identified you as an important participant in this system.\n\n"
    text += "To accept this invitation, simply click the following link and follow the instructions:\n\n{0}\n\n".format('the link')
    if len(request.form['message']) > 0:
        text += "The following message was included:\n\n{0}\n\n".format(request.form['message'])
    text += "Sincerely,\nThe ClimbSpotter.com Team"
    body = string.join((
        "From: invite@climbspotter.com",
        "To: %s" % to,
        "Subject: %s" % subject ,
        "",
        text
    ), "\r\n")
    server = smtplib.SMTP('localhost')
    server.sendmail('invite@climbspotter.com', [to], body)
    server.quit()

    flash('Invite sent')

    return redirect(url_for('invite_form'))
    

@app.route('/except')
def exc():

    raise NameError('HiThere')


@app.route('/u/user/activate')
@check_priv(1)
def user_activate():

    from model import User
    user_id = int(request.args.get('id'))
    user = User.User(user_id)
    user.activate()
    flash('User activated')
    return redirect(url_for('user'))

@app.route('/u/user/form/<username>')
@check_priv(1)
def user_form(username):

    from model import User
    user = User.getInstanceFromUsername(username)

    # Do not allow editing administrators
    if user.is_administrator():

        return redirect(url_for('user'))

    return render_template('user/form.html',
                username = user.username,
                original_username = user.username,
                email = user.email,
                display_name = user.display_name,
                active = user.active,
                role_ids = user.role_ids()
    )

@app.route('/u/user/save', methods = ['POST'])
@check_priv(1)
def user_save():

    from model import User

    # Load user id from original username
    user = User.getInstanceFromUsername(request.form['original_username'])

    errors = []
    # Validate data
    # Check for required fields
    labels = {'username': 'Username', 'email': 'E-mail', 'display_name': 'Display Name'}
    for el in ['username', 'email', 'display_name']:
        if el not in request.form or len(request.form[el]) == 0:
            errors.append("'{0}' is a required field.".format(labels[el]))

    # Make sure username is not currently used
    if user.username != request.form['username'] and User.usernameExists(request.form['username'], exclude_user_id = user.user_id):
        errors.append("The username '{username}' already exists in our system. Please choose a different one.".format(username = request.form['username']))

    # No spaces in username or password
    if ' ' in request.form['username']:
        errors.append('Username may not contain spaces')
    if len(request.form['username']) not in range(4, 31):
        errors.append('Username must be 4-30 characters long.')

    # If errors, display form again
    if len(errors) != 0:

        role_id = ''
        if 'role_id' in request.form and len(request.form['role_id']) > 0:
            role_id = int(request.form['role_id'])


        return render_template(
            'user/form.html', error = "<br/>\n".join(errors),
            original_username = request.form['original_username'],
            username = request.form['username'],
            email = request.form['email'],
            display_name = request.form['display_name'],
            active = int(request.form['active']),
            role_ids = [role_id]
        )

    # If no errors, save user as not active and redirect to awaiting approval page
    user.username = request.form['username']
    user.email = request.form['email']
    user.display_name = request.form['display_name']
    user.active = request.form['active']
    user.save()

    user.update_roles([request.form['role_id']])
    return redirect(url_for('user_manage'))

# Route form
@app.route('/u/route-work/form')
@app.route('/u/route-work/form/<route_work_id>')
@check_priv(2)
def route_work_form(route_work_id = None):

    route_work = None
    if route_work_id:

        from model import RouteWork
        route_work = RouteWork.RouteWork(route_work_id)

        # Redirect if not admin/moderator or user that created
        user = __authenticated_user()
        if not user.is_administrator() and not user.is_moderator() and route_work.user_id != user.user_id:

            return redirect(url_for('route_work_detail', route_work_id = route_work_id))

    return render_template(
        'route_work/form.html', 
        area_options = [('1', 'New River Gorge'), ('2', 'Meadow River Gorge')],
        route = route_work.get_route_name() if route_work else '',
        route_id = route_work.route_id if route_work else '',
        area = route_work.get_area_name() if route_work else '',
        area_id = route_work.get_area_id() if route_work else '',
        work_date = __sql_to_form(route_work.work_date) if route_work else '',
        who = route_work.who if route_work else '',
        bolts_placed = route_work.bolts_placed if route_work else '',
        anchor_replaced = route_work.anchor_replaced if route_work else '',
        new_anchor = route_work.new_anchor if route_work else '',
        route_work_id = route_work_id if route_work_id else '',
        info = route_work.info if route_work and route_work.info else ''
    )

# Route save
@app.route('/u/route-work/save', methods = ['POST'])
@check_priv(2)
def route_work_save():

    from model import RouteWork

    errors = []
    # Validate data
    # Check for required fields
    labels = {'area': 'Area', 'route': 'Route', 'work_date': 'Completed On', 'bolts_placed': 'Bolts', 'anchor': 'Anchor', 'info': 'Notes'}
    for el in ['area', 'route', 'work_date', 'bolts_placed']:
        if el not in request.form or len(request.form[el]) == 0:
            errors.append("'{0}' is a required field.".format(labels[el]))

    # Make sure route id matches route name
    if len(request.form['route_id']):
        from model import Route
        route = Route.Route(request.form['route_id'])
        if route.name != request.form['route']:
            errors.append("There was a problem finding the route that you entered, please try again.")

    # Make sure area id matches area name
    if len(request.form['area_id']):
        from model import Area
        area = Area.Area(request.form['area_id'])
        if (area.name != request.form['area']):
            errors.append('There was a problem finding the area that you entered, please try again.')

    # If errors, display form again
    if len(errors) != 0:

        return render_template(
            'route_work/form.html', error = "<br/>\n".join(errors),
            area_options = [('1', 'New River Gorge'), ('2', 'Meadow River Gorge')],
            route = request.form['route'],
            route_id = request.form['route_id'],
            area = request.form['area'],
            area_id = request.form['area_id'],
            work_date = request.form['work_date'],
            who = request.form['who'],
            bolts_placed = request.form['bolts_placed'],
            anchor_replaced = '1' if request.form['anchor'] == 'replaced' else '',
            new_anchor = '1' if request.form['anchor'] == 'new' else '',
            info = request.form['info']
        )

    # If no errors, save route work
    work = RouteWork.RouteWork(request.form['route_work_id'])
    work.route_id = request.form['route_id']
    work.work_date = __form_to_sql(request.form['work_date'])
    work.who = request.form['who']
    work.bolts_placed = request.form['bolts_placed'] if len(request.form['bolts_placed']) > 0 else '0'
    if request.form['anchor'] == 'replaced':
        work.anchor_replaced = 1
    else:
        work.anchor_replaced = 0
    if request.form['anchor'] == 'new':
        work.new_anchor = 1
    else:
        work.new_anchor = 0
    work.user_id = session['user_id']
    work.info = request.form['info']
    work.save()

    flash('Route work saved')

    return redirect(url_for('route_list'))

@app.route('/u/route-work/delete/<route_work_id>')
@check_priv(2)
def route_work_delete(route_work_id):

    from model import RouteWork
    rw = RouteWork.RouteWork(route_work_id)
    rw.delete()

    flash('Route work deleted')

    return redirect(url_for('route_list'))

# Route form
@app.route('/u/route-work/detail')
@app.route('/u/route-work/detail/<route_work_id>')
@check_priv(2)
def route_work_detail(route_work_id):

    from model import RouteWork
    route_work = RouteWork.RouteWork(route_work_id)

    return render_template(
        'route_work/detail.html',
        edit_priv = True if route_work.user_id == session['user_id'] else False,
        route = route_work.get_route_name(),
        area = route_work.get_area_name(),
        work_date = __sql_to_form(route_work.work_date),
        who = route_work.who,
        bolts_placed = route_work.bolts_placed,
        anchor_replaced = route_work.anchor_replaced,
        new_anchor = route_work.new_anchor,
        route_work_id = route_work_id,
        info = route_work.info
    )

# Suggest area
@app.route('/u/area/suggest')
@login_required
def area_suggest():

    from model import Area
    options = []
    for area in Area.search(request.args.get('term')):

       options.append({'label': area['name'], 'value': area['area_id']})

    return json.dumps(options)

# Suggest route
@app.route('/u/route/suggest')
@login_required
def route_suggest():

    from model import Route
    options = []
    for route in Route.search(request.args.get('term'), request.args.get('area_id')):

        options.append({'label': route['name'], 'value': route['route_id']})

    return json.dumps(options)

# View route work data
@app.route('/u/route-work/list')
@check_priv(3)
def route_list():

    from model import RouteWork
    return render_template('route_work/index.html', routes = RouteWork.get_data())

# Logout
@app.route('/logout')
def logout():

    session.pop('username', None)
    session.pop('user_id', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 8080)

ADMINS = ['jonstjohn@gmail.com']
if not app.debug:
    import logging
    from logging.handlers import SMTPHandler
    mail_handler = SMTPHandler('127.0.0.1',
                               'error@climbspotter.com',
                               ADMINS, 'YourApplication Failed')
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)
