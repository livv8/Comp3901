from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
import os
from os.path import join, dirname, realpath
import csv
import MySQLdb.cursors

app = Flask(__name__)

app.config['DEBUG'] = True
#upload folder
UPLOAD_FOLDER = 'static/files'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#database
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'inventory'

mysql = MySQL(app)

print('database connected')

#Root url
@app.route("/")
def index():
    return render_template('upload.html')

#get the upload files
@app.route('/', methods =['POST'])
def upload():
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
        #set the file path
        uploaded_file.save(file_path)
        #save the file
        cursor =mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        csv_data = csv.reader(open(file_path))
    for row in csv_data:
        cursor.execute("""CREATE TABLE IF NOT EXISTS `Passthru` ( `Item_Name` varchar(94), `Department` varchar(20), `Qty` varchar(10), `Price` varchar(22)) DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;;""")
        cursor.execute("""INSERT INTO `Passthru` (Item_Name, Department, Qty, Price) VALUES ( %s, %s, %s, %s)""",row)
    print(row)

    cursor.close()
    print("DONE")

    return redirect(url_for("index"))

    
if __name__ == '__main__':
    app.run(port = 5000)