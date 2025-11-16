# db.py  (optional replacement, only if you add .env)
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "postcrossing")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

try:
    db.command("ping")
    print("✅ Connected to MongoDB Atlas successfully!")
except Exception as e:
    print("❌ Connection failed:", e)
