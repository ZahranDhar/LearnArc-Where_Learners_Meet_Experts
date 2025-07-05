from flask import Flask, request, render_template, session, redirect, url_for, jsonify
import boto3 
import datetime
from pymongo import MongoClient
import certifi
from flask_socketio import SocketIO, emit, join_room
from routes.Auth import AuthRoutes
from routes.Profile import ProfileRoutes
from routes.Expertise import  ExpertiseRoutes
from routes.Search import SearchRoutes
from routes.Welcome import WelcomeRoutes
from routes.chat import ChatRoutes
from routes.chatlist import ChatListRoutes

# # Connecting to AWS Server
s3 = boto3.client('s3', aws_access_key_id='', aws_secret_access_key='', region_name='eu-north-1' )

# Connecting to MongoDB
client = MongoClient("")
client = MongoClient("")
db = client["LearnArc-StorageMongoDB"]
collection = db["Profiles"]
users_col = db["Profiles"]     # Reference to users collection
chats_col = db["Chats"]        # You should create this collection in MongoDB

# Initializations
app = Flask(__name__)
app.secret_key= ''
socketio = SocketIO(app)

# Initializing Routes
WelcomeRoutes(app)
AuthRoutes(app,db,s3)
ProfileRoutes(app,db)
ExpertiseRoutes(app,db)
SearchRoutes(app,db)
ChatRoutes(app,db,socketio)
ChatListRoutes(app, db)


@app.route('/home')
def home():
    current_user = users_col.find_one({"username": session['username']})
    all_users = list(users_col.find())

    print(f"Logged in as: {current_user['username']}")
    print("Other users in DB:")
    for user in all_users:
      print(f"- {user['username']}")

    return render_template('Home.html', current_user=current_user, users=all_users)


# Run the app
if __name__ == '__main__':
    socketio.run(app, debug=True)






