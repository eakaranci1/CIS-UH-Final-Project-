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

# Ingredients: 
@app.route("/ingredients", methods=["POST"])
def create_ingredient():
    data = request.get_json() or {}
    name = data.get("ingredientname")
    total = data.get("totalamount", 0)
    ok, last_id, _ = execute_query(
        connection,
        "INSERT INTO ingredient (ingredientname, totalamount) VALUES (%s,%s)",
        (name, total),
    )
    row = execute_read_query(connection, "SELECT * FROM ingredient WHERE id=%s", (last_id,))
    return jsonify(row[0]), 201

@app.route("/ingredients", methods=["GET"])
def list_ingredients():
    rows = execute_read_query(connection, "SELECT * FROM ingredient ORDER BY ingredientname ASC")
    return jsonify(rows)

@app.route("/ingredients/<int:iid>", methods=["GET"])
def get_ingredient(iid):
    rows = execute_read_query(connection, "SELECT * FROM ingredient WHERE id=%s", (iid,))
    return (jsonify(rows[0]), 200) if rows else (jsonify({"not found"}), 404)

@app.route("/ingredients/<int:iid>", methods=["PUT"])
def update_ingredient(iid):
    data = request.get_json() or {}
    fields, params = [], []
    if "ingredientname" in data:
        fields.append("ingredientname=%s"); params.append(data["ingredientname"])
    if "totalamount" in data:
        fields.append("totalamount=%s"); params.append(data["totalamount"])
    if not fields:
        return jsonify({"no fields"}), 400
    params.append(iid)
    ok, _, count = execute_query(connection, f"UPDATE ingredient SET {', '.join(fields)} WHERE id=%s", tuple(params))
    if not ok or count == 0:
        return jsonify({"update failed"}), 400
    row = execute_read_query(connection, "SELECT * FROM ingredient WHERE id=%s", (iid,))
    return jsonify(row[0])

@app.route("/ingredients/<int:iid>", methods=["DELETE"])
def delete_ingredient(iid):
    ok, _, _ = execute_query(connection, "DELETE FROM ingredient WHERE id=%s", (iid,))
    return ("", 204) if ok else (jsonify({"delete failed"}), 400)
