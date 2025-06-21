from flask import Flask, request, render_template, session
import os
from pymongo import MongoClient
import bcrypt
import boto3

# Connecting to AWS Server
s3 = boto3.client('s3', aws_access_key_id='', aws_secret_access_key='', region_name='eu-north-1' )

# Connecting to MongoDB
client = MongoClient("")
db = client["LearnArc-StorageMongoDB"]
profiles = db["Profiles"]
expertises = db["Expertises"]

# Handle Open Website Request
app = Flask(__name__)
app.secret_key= ''
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

    # Check if username is available
    if(profiles.find_one({"username":request.form['username']}) is not None):
        return render_template('signup.html')

    # Secure Password
    securepassword = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())

    # Upload Profile Picture to AWS
    file = request.files['profilepicture']
    if file:
        url = uploadProfilePictureToAWS(file)

    profiles.insert_one({"name": request.form['name'], "username": request.form['username'],"age": request.form['age'],"securepassword": securepassword,"profilepictureurl": url,"expertiseIDs":[]})
    
    session['username']=request.form['username']
    return render_template('expertise.html')

@app.route('/login',methods=['POST'])
def logIn():

    # Verify Password
    if(profiles.find_one({"username":request.form['username']}) is not None):

        user=profiles.find_one({"username":request.form['username']})    

        if(bcrypt.checkpw(request.form['password'].encode('utf-8'), user.get("securepassword"))):
            
            session['username']=request.form['username']
            return render_template('expertise.html')
        

@app.route('/add', methods=['POST'])
def addExpertise():

    result=expertises.insert_one({"course":request.form['course'],"title":request.form['title'],"description":request.form['description'],"rating":0})
    profiles.update_one({"username":session.get('username')},{"$push":{"expertiseIDs":result.inserted_id}})

    return render_template('home.html')






# Runs app
if __name__ == '__main__':
    app.run(debug=True)
