from flask import Flask, request, render_template, session, redirect, url_for, jsonify
import os
import bcrypt
import boto3
import certifi 
import datetime
from pymongo import MongoClient
from flask_socketio import SocketIO, emit, join_room

# Connecting to AWS Server
s3 = boto3.client('s3', aws_access_key_id='', aws_secret_access_key='', region_name='eu-north-1' )

# Connecting to MongoDB
client = MongoClient("")
db = client["LearnArc-StorageMongoDB"]
profiles = db["Profiles"]
expertises = db["Expertises"]
collection = db["Profiles"]
users_col = db["Profiles"]     # Reference to users collection
chats_col = db["Chats"]        # You should create this collection in MongoDB

# Handle Open Website Request
app = Flask(__name__)
app.secret_key= ''
socketio = SocketIO(app)  # Enables SocketIO support

@app.route('/')
def welcome():

    return render_template("signup.html")

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

    profiles.insert_one({"name": request.form['name'], "username": request.form['username'],"age": request.form['age'],"securepassword": securepassword,"profilepictureurl": url,"expertiseIDs":[], "chatUsernames":[]})
    user=profiles.find_one({"username":request.form['username']})
    session['username']=request.form['username']
    return render_template('Home.html',user=user)

@app.route('/login',methods=['POST'])
def logIn():

    # Verify Password
    if(profiles.find_one({"username":request.form['username']}) is not None):

        user=profiles.find_one({"username":request.form['username']})    

        if(bcrypt.checkpw(request.form['password'].encode('utf-8'), user.get("securepassword"))):
            
            session['username']=request.form['username']
            return render_template('Home.html',user=user)
        

@app.route('/add', methods=['POST'])
def addExpertise():

    result=expertises.insert_one({"username":session.get('username'),"course":request.form['course'],"title":request.form['title'],"description":request.form['description']})
    profiles.update_one({"username":session.get('username')},{"$push":{"expertiseIDs":result.inserted_id}})

    return render_template('home.html')

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

# Display Profile (Visiting and Personal)
@app.route('/profile',methods=['POST'])
def getProfile():

    # Retrieve user data from MongoDB
    user=profiles.find_one({"username":request.args.get('username')})
    user['_id']=str(user['_id'])

    issideprofile=request.args.get('isSideProfile').lower()=='true'
    if(issideprofile==False):
        expertiseIDs=user.get("expertiseIDs",[])
        expertiseList=list(expertises.find({"_id":{"$in":expertiseIDs}}))


        for expertise in expertiseList:
            expertise['_id'] = str(expertise['_id'])

        return jsonify({
        "expertiseList": expertiseList,
        "user": user
        })
    
    return jsonify(user)

# Display searched/course expertises
@app.route('/search',methods=['GET'])
def displaySearch():
    iscourse=request.args.get('isCourse').lower()=='true'

    if(iscourse):
        expertiseList=list(expertises.find({"course":request.args.get('courseName')}))
    else:
        expertiseList=list(expertises.find({"title":request.args.get('expertiseTitle')}))

    for expertise in expertiseList:
      expertise['_id'] = str(expertise['_id'])

    return jsonify(expertiseList)






# Run the app
if __name__ == '__main__':
    socketio.run(app, debug=True)


