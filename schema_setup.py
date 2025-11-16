from db import db

# User collection structure
user_schema = {
    "user_id": str,
    "username": str,
    "email": str,
    "address": str,
    "country": str,
    "registered_date": str,
    "sent_count": int,
    "received_count": int,
    "postcards_sent": list,
    "postcards_received": list
}

# Postcard collection structure
postcard_schema = {
    "postcard_id": str,
    "sender_id": str,
    "receiver_id": str,
    "message": str,
    "image_url": str,
    "sent_date": str,
    "received_date": str,
    "status": str  # "sent" | "received" | "pending"
}

# Transaction collection structure
transaction_schema = {
    "txn_id": str,
    "postcard_id": str,
    "sender_id": str,
    "receiver_id": str,
    "timestamp": str,
    "status": str  # "initiated" | "completed" | "failed"
}

# Create collections if not existing
db.create_collection("users") if "users" not in db.list_collection_names() else None
db.create_collection("postcards") if "postcards" not in db.list_collection_names() else None
db.create_collection("transactions") if "transactions" not in db.list_collection_names() else None

print("✅ Schema setup complete: users, postcards, transactions.")
