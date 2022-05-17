from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_mysqldb import MySQL
from authlib.integrations.flask_client import OAuth
from flask_paginate import Pagination, get_page_parameter
from passlib.hash import sha256_crypt
import MySQLdb.cursors
import re
import os
from os.path import join, dirname, realpath
import csv
import MySQLdb.cursors


app = Flask(__name__)
oauth = OAuth(app)
app.config['DEBUG']= True

app.secret_key = 'your secret key'

#upload file
UPLOAD_FOLDER = 'static/files'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'inventory'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'


mysql = MySQL(app)

@app.route("/adminlogin", methods=['GET','POST'])
def adminlogin():
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM adminaccounts WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            return redirect(url_for('index'))
        else:
            # Account doesnt exist or username/password incorrect
            flash("Incorrect username/password",category='error')
    # Show the login form with message (if any)
    return render_template("adminlogin.html")

@app.route("/adminsignup",  methods=['GET', 'POST'])
def adminsignup():
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
        cursor.execute('SELECT * FROM adminaccounts WHERE username = %s', (username,))
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
            cursor.execute('INSERT INTO adminaccounts VALUES (NULL, %s, %s, %s)', (username, password, email,))
            mysql.connection.commit()
            flash('You have successfully registered!')
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        flash( 'Please fill out the form!')
    # Show registration form with message (if any)        
    return render_template("adminsignup.html", msg=msg)

@app.route("/admin")
def admin():
    return render_template("adminbase.html")
#Root url
@app.route("/up")
def index():
    flash('File uploaded')
    return render_template('upload.html')

#get the upload files
@app.route('/up', methods =['POST'])
def upload():
    msg = ''
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
        #set the file path
        uploaded_file.save(file_path)
        #save the file
        cursor =mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        csv_data = csv.reader(open(file_path))
    for row in csv_data:
        cursor.execute("""CREATE TABLE IF NOT EXISTS `inventory_fil_i_tech` ( `Item_Name` varchar(20),`Item_Description` varchar(20), `Department` varchar(10), `Qty` varchar(22),`Price` varchar(22)) DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;;""")
        cursor.execute("""INSERT INTO `inventory_fil_i_tech` ( Item_Name,Item_Description,Department,Qty, Price) VALUES ( %s, %s, %s, %s)""",row)
   
        
    cursor.close()
    return redirect(url_for("index"))

@app.route('/update', methods=["GET","POST"])
def update():
    if request.method == 'POST':
        itemnumber = request.form['itemnumber']
        itemname = request.form['itemname']
        quantity = request.form['quantity']
        price = request.form['price']
        department = request.form['department']
        image = request.form['image']
 
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('UPDATE stores SET Item_Description=%s, Qty=%s, Price=%s, Department=%s, image=%s WHERE id=%s',(itemnumber, itemname, quantity,price,department,image))
    mysql.connection.commit()

    # flash('%s deleted'(table), 'success')
    return redirect(url_for('list'))

@app.route('/delete/<string:id>')
def delete_user(id):
  
 
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("DELETE FROM stores WHERE Item_Number=%s", (id,))
    mysql.connection.commit()

    # flash('%s deleted'(table), 'success')
    return redirect(url_for('list'))

@app.route('/list',methods=(['GET','POST']))
def list():
     # Create variables for easy access
    if request.method == 'POST':
        itemnumber = request.form['itemnumber']
        itemname = request.form['itemname']
        quantity = request.form['quantity']
        price = request.form['price']
        department = request.form['department']
        image = request.form['image']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute('INSERT INTO stores VALUES (%s, %s, %s, %s, %s, %s)', (itemnumber, itemname, quantity,price,department,image))
        mysql.connection.commit()
    
    search = False
    q = request.args.get('q')
    if q:
        search = True

    page = request.args.get(get_page_parameter(),default= 1, type=int)
    limit = 20
    offset = page*limit - limit
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM  `stores` ORDER By SKU ASC LIMIT %s OFFSET %s", (limit, offset))
    data=cursor.fetchall()
    total = cursor.execute("SELECT * FROM `stores` WHERE 1;")

    
    cursor.close()
    pagination = Pagination(page=page,per_page=limit, total=total, record_name='data')
    return render_template("product_list.html", data=data, pagination=pagination)

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
    # User is not loggedin redirect to login page
    user = session.get('user')
    return render_template("home.html")
    

@app.route("/details")
def details():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
     
    cursor.execute("SELECT * FROM `inventory_fil_i_tech` WHERE 1") 
    data=cursor.fetchall()
    cursor.close()
    return render_template("details.html", data=data)

@app.route("/books",methods=['GET', 'POST'])
def test():
    search = False
    q = request.args.get('q')
    if q:
        search = True

    page = request.args.get(get_page_parameter(),default= 1, type=int)
    limit = 6
    offset = page*limit - limit
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
     
    cursor.execute("SELECT * FROM `stores` WHERE `Department`= 'books' ORDER By Item_Number ASC LIMIT %s OFFSET %s", (limit, offset))
    data=cursor.fetchall()
    total = cursor.execute("SELECT * FROM `stores` WHERE 1;")
    cursor.close()
    
    pagination = Pagination(page=page,per_page=limit, total=total, record_name='data')
    return render_template("categories.html",data=data,pagination=pagination)

@app.route("/search")
def search():
     # search = False
    q = request.args.get('q')
    if q:
        search = True

    page = request.args.get(get_page_parameter(),default= 1, type=int)
    limit = 6
    offset = page*limit - limit
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
     
    cursor.execute("SELECT * FROM  `stores` ORDER By Item_Number ASC LIMIT %s OFFSET %s", (limit, offset))
    data=cursor.fetchall()
    total = cursor.execute("SELECT * FROM `stores` WHERE 1;")
    cursor.close()
    
    pagination = Pagination(page=page,per_page=limit, total=total, record_name='data')
    return render_template("productsview.html", pagination=pagination, data = data)

@app.route("/products",methods=["POST","GET"])
def products():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        search_word = request.form['query']
        print(search_word)
        if search_word == '':
            query = "SELECT * FROM stores;"
            cur.execute(query)
            data = cur.fetchall()
        else:    
            query = " SELECT * FROM stores WHERE Item_Description LIKE '%{}%' OR Price LIKE '%{}%' OR Qty LIKE '%{}%' OR Category LIKE '%{}%' OR Item_Type LIKE '%{}%' ORDER BY Item_Description DESC LIMIT 20".format(search_word,search_word,search_word,search_word,search_word)
            cur.execute(query)
            numrows = int(cur.rowcount)
            data = cur.fetchall()
            print(numrows)


   
    return jsonify({'htmlresponse':  render_template("search.html",numrows=numrows, data=data)})

@app.route("/geolocation")
def geo():
    return render_template("geolocation.html")

@app.route("/stores")
def stores():
    return render_template("stores.html")    

@app.route("/old_harbour")
def old():
     # Set the pagination configuration
    search = False
    q = request.args.get('q')
    if q:
        search = True

    page = request.args.get(get_page_parameter(),default= 1, type=int)
    limit = 6
    offset = page*limit - limit
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
     
    cursor.execute("SELECT * FROM  `inventory_fil_i_tech` ORDER By Item_Number ASC LIMIT %s OFFSET %s", (limit, offset))
    data=cursor.fetchall()
    total = cursor.execute("SELECT * FROM `inventory_fil_i_tech` WHERE 1;")
    cursor.close()
    
    pagination = Pagination(page=page,per_page=limit, total=total, record_name='data')
    return render_template("Old_Harbour.html", pagination=pagination, data=data) 

@app.route("/passthru")
def passthru():
    # Set the pagination configuration
    search = False
    q = request.args.get('q')
    if q:
        search = True

    page = request.args.get(get_page_parameter(),default= 1, type=int)
    limit = 6
    offset = page*limit - limit
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
     
    cursor.execute("SELECT * FROM  `passthru` ORDER By Item_Number ASC LIMIT %s OFFSET %s", (limit, offset))
    data=cursor.fetchall()
    total = cursor.execute("SELECT * FROM `passthru` WHERE 1;")
    cursor.close()
    
    pagination = Pagination(page=page,per_page=limit, total=total, record_name='data')
    return render_template("Passthru.html", pagination = pagination, data=data) 

@app.route("/lupin")
def lupin():
    # Set the pagination configuration
    search = False
    q = request.args.get('q')
    if q:
        search = True

    page = request.args.get(get_page_parameter(),default= 1, type=int)
    limit = 6
    offset = page*limit - limit
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
     
    cursor.execute("SELECT * FROM  `lupin` ORDER By Item_Number ASC LIMIT %s OFFSET %s", (limit, offset))
    data=cursor.fetchall()
    total = cursor.execute("SELECT * FROM `lupin` WHERE 1;")
    cursor.close()
    
    pagination = Pagination(page=page,per_page=limit, total=total, record_name='data')
    return render_template("lupin.html", pagination=pagination, data=data) 

@app.route("/acrostra")
def acrostra():
     # Set the pagination configuration
    search = False
    q = request.args.get('q')
    if q:
        search = True

    page = request.args.get(get_page_parameter(),default= 1, type=int)
    limit = 6
    offset = page*limit - limit
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
     
    cursor.execute("SELECT * FROM  `acrostra` ORDER By Item_Number ASC LIMIT %s OFFSET %s", (limit, offset))
    data=cursor.fetchall()
    total = cursor.execute("SELECT * FROM `acrostra` WHERE 1;")
    cursor.close()
    
    pagination = Pagination(page=page,per_page=limit, total=total, record_name='data')
    return render_template("Acrostra.html", pagination=pagination, data=data) 
if __name__ == '__main__':
    app.run(port=500)