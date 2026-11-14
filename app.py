
from flask import Flask, jsonify, request
from pymongo import MongoClient
from dotenv import load_dotenv
from pymongo.errors import PyMongoError
import json
import os

app = Flask(__name__)

# Load environment variables from .env
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

# Connect to MongoDB Atlas
if not MONGO_URI:
    raise ValueError("MONGO_URI is missing from the .env file")

client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=10000
)

db = client["mydatabase"]
collection = db["form_data"]


# Test MongoDB connection
try:
    client.admin.command("ping")
    print("SUCCESS: MongoDB Atlas connected!")
    print("Database:", db.name)
    print("Collection:", collection.name)
except PyMongoError as e:
    print("MongoDB connection failed:", e)


# Existing GET API
@app.route('/api', methods=['GET'])
def get_data():

    file_path = os.path.join(
        os.path.dirname(__file__), 'data.json'
    )

    try:
        with open(file_path, 'r') as file:
            data = json.load(file)

        return jsonify(data)

    except (FileNotFoundError, json.JSONDecodeError):
        return jsonify({"error": "Unable to read data.json"}), 500


# To-Do POST API
@app.route('/submittodoitem', methods=['POST'])
def submit_todo_item():

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "JSON data is required"
        }), 400

    item_name = data.get('itemName')
    item_description = data.get('itemDescription')

    if not item_name or not item_description:
        return jsonify({
            "error": "Item Name and Item Description are required"
        }), 400

    todo_item = {
        "itemName": item_name,
        "itemDescription": item_description
    }

    try:
        result = collection.insert_one(todo_item)

        return jsonify({
            "message": "To-Do item saved successfully",
            "id": str(result.inserted_id)
        }), 201

    except PyMongoError as e:
        return jsonify({
            "error": "Database insertion failed",
            "details": str(e)
        }), 500


if __name__ == '__main__':
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True,
        use_reloader=False
    )



