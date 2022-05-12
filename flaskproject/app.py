from flask import Flask, render_template, request, redirect, url_for, session, Blueprint
from flask_mysqldb import MySQL
from authlib.integrations.flask_client import OAuth
from flask_paginate import Pagination, get_page_parameter
from passlib.hash import sha256_crypt
import MySQLdb.cursors
import re


app = Flask(__name__)
oauth = OAuth(app)
app.config['DEBUG']= True

app.secret_key = 'your secret key'


# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'inventory'

mysql = MySQL(app)

@app.route("/")
def base():
    return render_template("start.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = "The username or password incorrect or Account doesn't exist"
    # Show the login form with message (if any)
    return render_template('login.html', msg=msg)

    # http://localhost:5000/python/logout - this will be the logout page
@app.route('/pythonlogin/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   session.pop('user', None)

   # Redirect to login page
   return redirect(url_for('login'))

@app.route("/signup",  methods=['GET', 'POST'])
def signup():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = sha256_crypt.encrypt( request.form['password'])
        email = request.form['email']

        # Check if account exists using MySQL        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)        
    return render_template("signup.html", msg=msg)

@app.route('/google/')
def google():
   
    # Google Oauth Config
    # Get client_id and client_secret from environment variables
    # For developement purpose you can directly put it
    # here inside double quotes
    GOOGLE_CLIENT_ID = '843084466858-rrdrv4sq0gd11lhsmqeqdn9n4topcorg.apps.googleusercontent.com'
    GOOGLE_CLIENT_SECRET = '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'
     
    CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
    oauth.register(
        name='google',
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url=CONF_URL,
        client_kwargs={
            'scope': 'openid email profile'
        }
    )
     
    # Redirect to google_auth function
    redirect_uri = url_for('google_auth', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)
 
@app.route('/google/auth/')
def google_auth():
    token = oauth.google.authorize_access_token()
    user = token.get('userinfo')
    if user:
        session['user'] = user    
    return redirect("/home")
 
           
@app.route("/home")
def home():
    # Check if user is loggedin
    # if 'loggedin' in session:
    #     # User is loggedin show them the home page
    #     return render_template('home.html', username=session['username'])
    # # User is not loggedin redirect to login page
    user = session.get('user')
    return render_template("home.html")
    

@app.route("/details")
def details():
    return render_template("details.html")

@app.route("/categories")
def test():
    return render_template("categories.html")

@app.route("/start")
def start():
    return render_template("start.html")

@app.route("/product_list")
def products():
    # Set the pagination configuration
    search = False
    q = request.args.get('q')
    if q:
        search = True

    page = request.args.get(get_page_parameter(),default= 1, type=int)
    limit = 20
    offset = page*limit - limit
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
     
    cursor.execute("SELECT * FROM  `inventory_fil_i_tech` ORDER By Item_Number ASC LIMIT %s OFFSET %s", (limit, offset))
    data=cursor.fetchall()
    total = cursor.execute("SELECT * FROM `inventory_fil_i_tech` WHERE 1;")
    cursor.close()
    
    pagination = Pagination(page=page,per_page=limit, total=total, record_name='data')
    return render_template("product_list.html", pagination=pagination, data=data)

    
@app.route('/productslist')
def productlist():
    search = False
    q = request.args.get('q')
    if q:
        search = True

    page = request.args.get(get_page_parameter(),default= 1, type=int)
    limit = 20
    offset = page*limit - limit
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
     
    cursor.execute("SELECT * FROM  `inventory_fil_i_tech` ORDER By Item_Number ASC LIMIT %s OFFSET %s", (limit, offset))
    data=cursor.fetchall()
    total = cursor.execute("SELECT * FROM `inventory_fil_i_tech` WHERE 1;")
    cursor.close()
    
    pagination = Pagination(page=page,per_page=limit, total=total, record_name='data')
    return render_template("products2.html", pagination=pagination, data=data)
        
if __name__ == '__main__':
    app.run(port=500)