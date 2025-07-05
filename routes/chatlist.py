# routes/chatlist.py

from flask import Blueprint, session, render_template, redirect
from pymongo import DESCENDING

def ChatListRoutes(app, db):
    chatlist_bp = Blueprint("chatlist", __name__)
    chats_col = db["Chats"]

    @chatlist_bp.route("/chatlist")
    def chat_list():
        current_user = session.get("username")
        if not current_user:
            return redirect("/login")

        chats = chats_col.find({
            "$or": [
                {"sender": current_user},
                {"receiver": current_user}
            ]
        }).sort("timestamp", DESCENDING)

        seen = set()
        recent_partners = []

        for chat in chats:
            partner = chat["receiver"] if chat["sender"] == current_user else chat["sender"]
            if partner not in seen:
                seen.add(partner)
                recent_partners.append({
                    "username": partner,
                    "last_message": chat["message"],
                    "timestamp": chat["timestamp"]
                })

        return render_template("chatlist.html", chat_partners=recent_partners)

    app.register_blueprint(chatlist_bp)
