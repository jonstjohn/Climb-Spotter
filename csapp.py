from flask import Flask
from flask import render_template
from flask import request, session
from flask import abort, redirect, url_for

import sqlalchemy
import json
import db

app = Flask(__name__)
app.debug = True

# set the secret key.  keep this really secret:
app.secret_key = 'ADDefA221 -9981 Bdd%kkkll'

@app.route('/')
def index(post_id = None, slug = None):

    return render_template('index.html')


@app.route('/register')
def register():

    return render_template('register.html')

@app.route('/doRegister', methods=['POST'])
def doRegister():

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
    return 'no error'


@app.route('/registerDone')
def registerDone():

    return render_template('registerDone.html')
    

@app.route('/doLogin', methods=['POST'])
def doLogin():
    from model import User

    try:
        user = User.getInstanceFromUsernamePassword(request.form['username'], request.form['password'])
        session['username'] = user.username
        return redirect(url_for('user'))
    except sqlalchemy.orm.exc.NoResultFound:
        return redirect(url_for('index'))

@app.route('/u')
def user():

    from model import User
    return render_template('user/index.html', users = User.getData())

# Logout
@app.route('/logout')
def logout():

    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/feed/ios/news.json')
def news():

    page = 0
    if request.args.get('page'):
        page = int(request.args.get('page'))

    articles = _get_articles(page, 20)
    return json.dumps(articles)

@app.route('/feed/ios/article')
def article():

    news_id = request.args.get('id')
    return render_template('article.html', article = _get_article(news_id)) 

@app.route('/news/listing')
def newsListing():

    return render_template('newsListing.json')

@app.route('/video/listing')
@app.route('/video/listing/<page>')
def videoListing(page = 1):

    return render_template("videos%s.json" % (page))

@app.route('/video/youtube')
def videoYouTube():

    return render_template('youtube.html')

@app.route('/video/vimeo')
def videoVimeo():
    
    return render_template('vimeo.html')

def _get_db():

    return MySQLdb.connect(
        host='localhost',
        user = 'dpm',
        passwd = 'dpm',
        db = 'dpm',
        cursorclass=MySQLdb.cursors.DictCursor
    )

def _get_articles(page = 0, per_page = 20):

    db = _get_db()
    cursor = db.cursor()
    start = page * per_page
    sql = "SELECT news_id, title, teaser, date_format(posted, '%%m/%%d/%%y') as post, thumb, url FROM dpm.news ORDER BY posted DESC LIMIT %i, %i" % (start, per_page)
    cursor.execute(sql)
    return cursor.fetchall()

def _get_article(news_id):

    db = _get_db()
    cursor = db.cursor()
    sql = "SELECT title, posted, posted_by, detail FROM dpm.news WHERE news_id = %s"
    cursor.execute(sql, (news_id))

    article = cursor.fetchone()
    article['detail'] = _cleanup_detail(article['detail'])
    return article

def _cleanup_detail(detail):

    import re

    # Resolve relative paths
    detail = detail.replace('src="/', 'src="http://www.dpmclimbing.com/')

    # Re-size images
    detail = re.sub(r'width: ([0-9]+)px; height: ([0-9]+)px;?', _resize_img, detail)

    return detail

def _resize_img(m):

    #width = m.group(1)
    #height = m.group(2)
    return 'width: 300px'
        
if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 8080)

# set the secret key.  keep this really secret:
#app.secret_key = 'ADDefA221 -9981 Bdd%kkkll'
