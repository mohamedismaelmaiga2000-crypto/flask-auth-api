from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import bcrypt

app = Flask(__name__)

# DB CONFIG
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# JWT CONFIG
app.config["JWT_SECRET_KEY"] = "change-this-secret-key"

db = SQLAlchemy(app)
jwt = JWTManager(app)

# MODEL
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(200))


# REGISTER
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    hashed_pw = bcrypt.hashpw(
        data['password'].encode('utf-8'),
        bcrypt.gensalt()
    )

    user = User(
        username=data['username'],
        email=data['email'],
        password=hashed_pw.decode('utf-8')
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered"}), 201


# LOGIN
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    user = User.query.filter_by(email=data['email']).first()

    if not user:
        return jsonify({"message": "User not found"}), 404

    if bcrypt.checkpw(
        data['password'].encode('utf-8'),
        user.password.encode('utf-8')
    ):
        token = create_access_token(identity=str(user.id))
        return jsonify({"token": token})

    return jsonify({"message": "Invalid credentials"}), 401


# PROFILE (PROTECTED)
@app.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    return jsonify({
        "username": user.username,
        "email": user.email
    })


# CREATE DB + RUN SERVER
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)