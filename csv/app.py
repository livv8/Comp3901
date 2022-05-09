from flask import Flask, render_template, request, redirect, url_for
import os
from os.path import join, dirname, realpath

import pandas as pd 
import mysql.connector

app = Flask(__name__)


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

mycursor = mydb.cursor()

mycursor.execute("SHOW DATABASES")

#view All Database
for x in mycursor:
    print(x)


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
    return redirect(url_for("index"))

def parseCSV(filePath):
    #cvs column Names
    col_names = ['item_Number', 'item_Description', 'Qty', 'Price', 'Department']
    #use pandas to parse the csv file
    csvData = pd.read_csv(filePath,names=col_names, header=None)
    #Loop through the Rows
    for i,row in csvData.iterrows():
        sql = "INSERT INTO store (item_Number, item_Description, Qty, Price, Department) VALUES (%s, %s, %s, %s, %s, %s)"
        value = (row['item_Number'],row['item_Description'],row['Qty'],row['Price'],row['Department'])
        mycursor.execute(sql, value, if_exists='append')
        mydb.commit()
        print(i,row['item_Number'],row['item_Description'],row['Qty'],row['Price'],row['Department'])


if __name__ == '__main__':
    app.run(port = 5000)