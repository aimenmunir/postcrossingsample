from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from db import db
import random
from datetime import datetime
from bson import ObjectId
app = Flask(__name__)
CORS(app)  
@app.route("/register", methods=["POST"])
def register_user():
    name = request.form.get("name")
    email = request.form.get("email")
    country = request.form.get("country")
    address = request.form.get("address")
    if not name or not email:
        return jsonify({"error": "Name and email are required"}), 400
    if db.users.find_one({"username": name}):
        return jsonify({"error": f"User '{name}' already exists"}), 409
    user = {
        "user_id": str(ObjectId()),
        "username": name,
        "email": email,
        "address": address or "N/A",
        "country": country or "N/A",
        "registered_date": datetime.utcnow(),
        "sent_count": 0,
        "received_count": 0,
        "postcards_sent": [],
        "postcards_received": []
    }
    db.users.insert_one(user)
    return jsonify({"message": f" User {name} registered successfully!"}), 201
@app.route('/users', methods=['GET'])
def get_users():
    try:
        users_cursor = db.users.find({}, {'_id': 0, 'username': 1, 'email': 1, 'country': 1})
        users = list(users_cursor)
        return jsonify(users), 200
    except Exception as e:
        print("Error fetching users:", e)
        return jsonify({"error": str(e)}), 500
@app.route("/add_postcard", methods=["POST"])
def add_postcard():
    try:
        code = request.form.get("code")
        message = request.form.get("message")
        image_url = request.form.get("image_url")
        sender = request.form.get("sender")
        if not code or not code.strip():
            return jsonify({"error": "Postcard ID (code) is required"}), 400
        if not sender or not sender.strip():
            return jsonify({"error": "Sender is required"}), 400
        if db.postcards.find_one({"postcard_id": code.strip()}):
            return jsonify({"error": f"Postcard '{code}' already exists"}), 409
        postcard = {
            "postcard_id": code.strip(),
            "sender_id": sender.strip(),
            "receiver_id": None,
            "message": message.strip() if message else "",
            "image_url": image_url.strip() if image_url else "",
            "sent_date": None,
            "received_date": None,
            "status": "pending"
        }

        db.postcards.insert_one(postcard)
        return jsonify({"message": f"Postcard '{code}' added successfully!"}), 201

    except Exception as e:
        print("Error adding postcard:", e)
        return jsonify({"error": str(e)}), 500
@app.route("/send_postcard", methods=["POST"])
def send_postcard():
    sender = request.form.get("sender")
    receiver = request.form.get("receiver")
    postcard_id = request.form.get("postcard_id")
    if not sender or not receiver or not postcard_id:
        return jsonify({"error": "Sender, receiver, and postcard ID are required"}), 400
    sender_user = db.users.find_one({"username": sender})
    receiver_user = db.users.find_one({"username": receiver})
    postcard = db.postcards.find_one({"postcard_id": postcard_id})
    if not sender_user:
        return jsonify({"error": f"Sender '{sender}' not found"}), 404
    if not receiver_user:
        return jsonify({"error": f"Receiver '{receiver}' not found"}), 404
    if not postcard:
        return jsonify({"error": f"Postcard '{postcard_id}' not found"}), 404
    db.postcards.update_one(
        {"postcard_id": postcard_id},
        {"$set": {
            "receiver_id": receiver,
            "sent_date": datetime.utcnow(),
            "status": "sent"
        }}
    )
    txn = {
        "txn_id": str(ObjectId()),
        "postcard_id": postcard_id,
        "sender_id": sender,
        "receiver_id": receiver,
        "timestamp": datetime.utcnow(),
        "status": "sent"
    }
    db.transactions.insert_one(txn)
    db.users.update_one(
        {"username": sender},
        {"$inc": {"sent_count": 1}, "$push": {"postcards_sent": postcard_id}}
    )
    db.users.update_one(
        {"username": receiver},
        {"$inc": {"received_count": 1}, "$push": {"postcards_received": postcard_id}}
    )
    other_users = list(db.users.find(
        {"username": {"$nin": [sender, receiver]}},
        {"_id": 0, "username": 1}
    ))
    reciprocal_msg = ""
    if other_users:
        reciprocal_sender = random.choice(other_users)["username"]
        available_postcards = list(db.postcards.find({
            "status": "pending",
            "postcard_id": {"$ne": postcard_id}
        }, {"_id": 0, "postcard_id": 1}))
        if available_postcards:
            reciprocal_postcard = random.choice(available_postcards)["postcard_id"]
            db.postcards.update_one(
                {"postcard_id": reciprocal_postcard},
                {"$set": {
                    "receiver_id": sender,
                    "sent_date": datetime.utcnow(),
                    "status": "sent"
                }}
            )
            db.transactions.insert_one({
                "txn_id": str(ObjectId()),
                "postcard_id": reciprocal_postcard,
                "sender_id": reciprocal_sender,
                "receiver_id": sender,
                "timestamp": datetime.utcnow(),
                "status": "sent"
            })

            db.users.update_one(
                {"username": reciprocal_sender},
                {"$inc": {"sent_count": 1}, "$push": {"postcards_sent": reciprocal_postcard}}
            )
            db.users.update_one(
                {"username": sender},
                {"$inc": {"received_count": 1}, "$push": {"postcards_received": reciprocal_postcard}}
            )
            reciprocal_msg = f" You’ll soon receive postcard '{reciprocal_postcard}' from {reciprocal_sender}!"
        else:
            reciprocal_msg = " No other pending postcards available for reciprocal sending."
    else:
        reciprocal_msg = " No other users available for reciprocal sending."
    return jsonify({
        "message": f" Postcard '{postcard_id}' sent to {receiver}! {reciprocal_msg}"
    }), 200
@app.route("/view_postcards", methods=["POST"])
def view_postcards():
    user = request.form.get("user")
    if not user:
        return jsonify({"error": "User required"}), 400
    received = list(db.transactions.find({"receiver_id": user}, {"_id": 0}))
    sent = list(db.transactions.find({"sender_id": user}, {"_id": 0}))
    return jsonify({
        "received": received,
        "sent": sent
    }), 200
@app.route("/")
def home():
    return render_template("index.html")
if __name__ == "__main__":
    print(" Flask app running on http://127.0.0.1:5000")
    app.run(debug=True)

