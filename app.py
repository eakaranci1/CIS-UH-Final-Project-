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
    return jsonify({"message": "API running!"})

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

# Recipes
@app.route("/recipes", methods=["POST"])
def create_recipe():
    data = request.get_json() or {}
    name = data.get("name")
    instructions = data.get("instructions") or ""
    ok, last_id, _ = execute_query(
        connection,
        "INSERT INTO recipe (name, instructions) VALUES (%s,%s)",
        (name, instructions),
    )
    if not ok:
        return jsonify({"insert failed"}), 400
    row = execute_read_query(connection, "SELECT * FROM recipe WHERE id=%s", (last_id,))
    return jsonify(row[0]), 201

@app.route("/recipes", methods=["GET"])
def list_recipes():
    rows = execute_read_query(connection, "SELECT * FROM recipe ORDER BY name ASC")
    for r in rows:
        r["ingredients"] = execute_read_query(connection, """
            SELECT ri.id, ri.ingredientid, i.ingredientname, ri.amount
            FROM recipeingredient ri
            JOIN ingredient i ON i.id = ri.ingredientid
            WHERE ri.recipeid=%s
        """, (r["id"],))
    return jsonify(rows)

@app.route("/recipes/<int:rid>", methods=["GET"])
def get_recipe(rid):
    rows = execute_read_query(connection, "SELECT * FROM recipe WHERE id=%s", (rid,))
    if not rows:
        return jsonify({"not found"}), 404
    r = rows[0]
    r["ingredients"] = execute_read_query(connection, """
        SELECT ri.id, ri.ingredientid, i.ingredientname, ri.amount
        FROM recipeingredient ri
        JOIN ingredient i ON i.id = ri.ingredientid
        WHERE ri.recipeid=%s
    """, (rid,))
    return jsonify(r)

@app.route("/recipes/<int:rid>", methods=["PUT"])
def update_recipe(rid):
    data = request.get_json() or {}
    fields, params = [], []
    if "name" in data: fields.append("name=%s"); params.append(data["name"])
    if "instructions" in data: fields.append("instructions=%s"); params.append(data["instructions"])
    if not fields: return jsonify({"no fields"}), 400
    params.append(rid)
    ok, _, count = execute_query(connection, f"UPDATE recipe SET {', '.join(fields)} WHERE id=%s", tuple(params))
    if not ok or count == 0: return jsonify({"update failed"}), 400
    row = execute_read_query(connection, "SELECT * FROM recipe WHERE id=%s", (rid,))
    return jsonify(row[0])

@app.route("/recipes/<int:rid>", methods=["DELETE"])
def delete_recipe(rid):
    ok, _, _ = execute_query(connection, "DELETE FROM recipe WHERE id=%s", (rid,))
    return ("", 204) if ok else (jsonify({"delete failed"}), 400)

# RecipeIngredients 
@app.route("/recipeingredients", methods=["POST"])
def create_recipeingredient():
    data = request.get_json() or {}
    rid = data.get("recipeid")
    iid = data.get("ingredientid")
    amt = data.get("amount")
    ok, last_id, _ = execute_query(connection, """
        INSERT INTO recipeingredient (recipeid, ingredientid, amount) VALUES (%s,%s,%s)
    """, (rid, iid, amt))
    if not ok:
        return jsonify({"insert failed"}), 400
    row = execute_read_query(connection, "SELECT * FROM recipeingredient WHERE id=%s", (last_id,))
    return jsonify(row[0]), 201

@app.route("/recipeingredients", methods=["GET"])
def list_recipeingredients():
    rows = execute_read_query(connection, "SELECT * FROM recipeingredient")
    return jsonify(rows)

@app.route("/recipeingredients/<int:riid>", methods=["GET"])
def get_recipeingredient(riid):
    rows = execute_read_query(connection, "SELECT * FROM recipeingredient WHERE id=%s", (riid,))
    return (jsonify(rows[0]), 200) if rows else (jsonify({"not found"}), 404)

@app.route("/recipeingredients/<int:riid>", methods=["PUT"])
def update_recipeingredient(riid):
    data = request.get_json() or {}
    fields, params = [], []
    if "recipeid" in data: fields.append("recipeid=%s"); params.append(data["recipeid"])
    if "ingredientid" in data: fields.append("ingredientid=%s"); params.append(data["ingredientid"])
    if "amount" in data: fields.append("amount=%s"); params.append(data["amount"])
    if not fields: return jsonify({"no fields"}), 400
    params.append(riid)
    ok, _, count = execute_query(connection,
        f"UPDATE recipeingredient SET {', '.join(fields)} WHERE id=%s", tuple(params))
    if not ok or count == 0: return jsonify({"update failed"}), 400
    row = execute_read_query(connection, "SELECT * FROM recipeingredient WHERE id=%s", (riid,))
    return jsonify(row[0])

@app.route("/recipeingredients/<int:riid>", methods=["DELETE"])
def delete_recipeingredient(riid):
    ok, _, _ = execute_query(connection, "DELETE FROM recipeingredient WHERE id=%s", (riid,))
    return ("", 204) if ok else (jsonify({"delete failed"}), 400)

