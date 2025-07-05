from flask import Flask, request, render_template, session, redirect, url_for, jsonify
import boto3 
import datetime
from pymongo import MongoClient
from flask_socketio import SocketIO, emit, join_room
from routes.Auth import AuthRoutes
from routes.Profile import ProfileRoutes
from routes.Expertise import  ExpertiseRoutes
from routes.Search import SearchRoutes
from routes.Welcome import WelcomeRoutes

# Connecting to AWS Server
s3 = boto3.client('s3',aws_access_key_id='', aws_secret_access_key='', region_name='eu-north-1' )

# Connecting to MongoDB
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

# Chat route
@app.route('/chat/<friend_username>')
def chat(friend_username):
    # Simulate login (for testing)
    if 'username' not in session:
        session['username'] = 'aidahrufai'  # 👈 Replace with valid test user

    # Get the current logged-in user
    current_user = users_col.find_one({"username": session['username']})
    if not current_user:
        return "Current user not found in DB", 404

    # Get the friend by username
    friend = users_col.find_one({"username": friend_username})
    if not friend:
        return f"Friend user '{friend_username}' not found in DB", 404

    # Get all chat messages between these two users
    messages = list(chats_col.find({
        "$or": [
            {"sender": session['username'], "receiver": friend_username},
            {"sender": friend_username, "receiver": session['username']}
        ]
    }).sort("timestamp", 1))

    # Render chat page with all required variables
    return render_template(
        'chat.html',
        current_user=current_user,
        friend=friend,
        messages=messages
    )
# @app.route('/')
# def welcome():
#     # Set a test session username
#     session['username'] = 'aidahrufai'

#     # Check that both users exist
#     current_user = users_col.find_one({"username": 'aidahrufai'})
#     friend = users_col.find_one({"username": 'behzad123'})

#     # Fallback: show error if either is missing
#     if not current_user or not friend:
#         return "Make sure both 'aidahrufai' and 'behzad123' exist in your MongoDB", 400

#     # Load messages between them
#     messages = list(chats_col.find({
#         "$or": [
#             {"sender": 'aidahrufai', "receiver": 'behzad123'},
#             {"sender": 'behzad123', "receiver": 'aidahrufai'}
#         ]
#     }).sort("timestamp", 1))

#     # Render chat page
#     return render_template('chat.html', current_user=current_user, friend=friend, messages=messages)


@app.route('/home')
def home():
    current_user = users_col.find_one({"username": session['username']})
    all_users = list(users_col.find())

    print(f"Logged in as: {current_user['username']}")
    print("Other users in DB:")
    for user in all_users:
      print(f"- {user['username']}")

    return render_template('Home.html', current_user=current_user, users=all_users)

# WebSocket Events
@socketio.on('join_chat')
def on_join(data):
    room = get_room_name(data['sender'], data['receiver'])
    print(f"[JOIN] {data['sender']} joined room {room}")
    join_room(room)

@socketio.on('send_message')
def handle_send_message(data):
    sender = data['sender']
    receiver = data['receiver']
    message = data['message']
    timestamp = datetime.datetime.utcnow()
    print(f"[MESSAGE] {sender} -> {receiver}: {message}")
   

    # Save to MongoDB
    chats_col.insert_one({
        "sender": sender,
        "receiver": receiver,
        "message": message,
        "timestamp": timestamp
    })

    room = get_room_name(sender, receiver)
    emit('receive_message', {
        'sender': sender,
        'message': message,
        'timestamp': timestamp.strftime("%H:%M")
    }, room=room)

def get_room_name(user1, user2):
    return "-".join(sorted([user1, user2]))

# Run the app
if __name__ == '__main__':
    socketio.run(app, debug=True)


