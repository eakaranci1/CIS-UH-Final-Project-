from flask import Flask, jsonify, request
from sql import create_connection, execute_query, execute_read_query
from creds import Creds

app = Flask(__name__)

# DB connection
connection = create_connection(
    Creds.conString,
    Creds.userName,
    Creds.password,
    Creds.dbName
)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"API running!"})
