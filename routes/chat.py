from flask import render_template, session
from flask_socketio import join_room, emit
import datetime

class ChatRoutes:
    def __init__(self, app, db, socketio):
        users_col = db["Profiles"]
        chats_col = db["Chats"]

        @app.route('/chat/<friend_username>')
        def chat(friend_username):
            if 'username' not in session:
                return "You are not logged in", 403

            current_user = users_col.find_one({"username": session['username']})
            if not current_user:
                return "Current user not found in DB", 404

            friend = users_col.find_one({"username": friend_username})
            if not friend:
                return f"Friend user '{friend_username}' not found in DB", 404

            messages = list(chats_col.find({
                "$or": [
                    {"sender": session['username'], "receiver": friend_username},
                    {"sender": friend_username, "receiver": session['username']}
                ]
            }).sort("timestamp", 1))

            return render_template(
                'chat.html',
                current_user=current_user,
                friend=friend,
                messages=messages
            )

        @socketio.on('join_chat')
        def on_join(data):
            room = self.get_room_name(data['sender'], data['receiver'])
            print(f"[JOIN] {data['sender']} joined room {room}")
            join_room(room)

        @socketio.on('send_message')
        def handle_send_message(data):
            sender = data['sender']
            receiver = data['receiver']
            message = data['message']
            timestamp = datetime.datetime.utcnow()
            print(f"[MESSAGE] {sender} -> {receiver}: {message}")

            chats_col.insert_one({
                "sender": sender,
                "receiver": receiver,
                "message": message,
                "timestamp": timestamp
            })

            room = self.get_room_name(sender, receiver)
            emit('receive_message', {
                'sender': sender,
                'message': message,
                'timestamp': timestamp.strftime("%H:%M")
            }, room=room)

    def get_room_name(self, user1, user2):
        return "-".join(sorted([user1, user2]))
