from flask import Flask, request, jsonify
from database import get_connection, create_users_table
from security import hash_password

app = Flask(__name__)

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"error": "All fields are required"}), 400

    password_hash = hash_password(password)

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, password_hash)
        )

        conn.commit()
        conn.close()

        return jsonify({"message": "User registered successfully"}), 201

    except Exception as e:
        return jsonify({"error": "User already exists"}), 409


if __name__ == "__main__":
    create_users_table()
    app.run(debug=True)