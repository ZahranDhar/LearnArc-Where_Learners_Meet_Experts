from flask import Flask, request, render_template
import os
from pymongo import MongoClient
import bcrypt
import boto3

# Connecting to AWS Server
s3 = boto3.client('s3', aws_access_key_id='', aws_secret_access_key='', region_name='eu-north-1' )

# Connecting to MongoDB
client = MongoClient("mongodb+srv://zahrannazirdhar:@cluster.wojbkyb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster")
db = client["LearnArc-StorageMongoDB"]
collection = db["Profiles"]

# Handle Open Website Request
app = Flask(__name__)
@app.route('/')
def welcome():

    return render_template('signup.html')

# Handle Signup Request 

# Uploads Profile picture to AWS
def uploadProfilePictureToAWS(fileObj):

    fileName = f"profile_pictures/{fileObj.filename}"
    bucketName = 'learnarc-storageaws'
    s3.upload_fileobj(fileObj, bucketName, fileName, ExtraArgs={'ContentType': fileObj.content_type})

    return f"https://{bucketName}.s3.amazonaws.com/{fileName}"

# Uploads Data to Databases
@app.route('/signUp', methods=['POST'])
def signUp():

    # Secure Password
    securepassword = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())

    # Upload Profile Picture to AWS
    file = request.files['profilepicture']
    if file:
        url = uploadProfilePictureToAWS(file)

    collection.insert_one({"name": request.form['name'], "username": request.form['username'],"age": request.form['age'],"securepassword": securepassword,"profilepictureurl": url})
    
    return render_template('Home.html')

# Runs app
if __name__ == '__main__':
    app.run(debug=True)
