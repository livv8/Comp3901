from flask import Flask, render_template, request, redirect, url_for
import os
from os.path import join, dirname, realpath
import csv
import mysql.connector

app = Flask(__name__)

app.config['DEBUG'] = True
#upload folder
UPLOAD_FOLDER = 'static/files'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#database
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="inventory"
)
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
        cursor =mydb.cursor()
    csv_data = csv.reader(open(file_path))
    for row in csv_data:
        cursor.execute("""INSERT INTO ohs (Item_Number, Item_Description, Qty, Price, Department) VALUES (%s, %s, %s, %s, %s)""",row)
    print(row)

    mydb.commit()
    cursor.close()
    print("DONE")

    return redirect(url_for("index"))

    
if __name__ == '__main__':
    app.run(port = 5000)