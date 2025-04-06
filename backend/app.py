from flask import Flask, render_template, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from supabase import create_client, Client

SUPABASE_URL = "https://chursupvkphjclbiaaky.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNodXJzdXB2a3BoamNsYmlhYWt5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDM1OTIyMTMsImV4cCI6MjA1OTE2ODIxM30.NvZT6GTK-hu7aUkD6l37Wo8jWK6LpdqNQqv2d6M4vg0"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__, template_folder="../frontend/templates", static_folder="../frontend/static")
app.config["JWT_SECRET_KEY"] = "1e0ceb6abcf50b4334c09eb184f0cec1f05ff73563c5dfe6f904f13cc8555b26"  # Replace with a secure key
jwt = JWTManager(app)

@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    # Create user in Supabase Auth
    response = supabase.auth.sign_up({"email": email, "password": password})
    if "error" in response:
        return jsonify({"error": response["error"]["message"]}), 400

    user = response.user
    user_id = user.id  # Access the user ID

    # Insert the user into the custom 'users' table
    supabase.table("users").insert({
        "id": user_id,
        "email": email
    }).execute()

    return jsonify({"message": "User created successfully!"}), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    # Authenticate user with Supabase Auth
    response = supabase.auth.sign_in_with_password({"email": email, "password": password})
    if "error" in response:
        return jsonify({"error": response["error"]["message"]}), 401
    
    user = response.user
    user_id = user.id  # Access the user ID
    # Generate JWT token
    access_token = create_access_token(identity=user_id)
    return jsonify({"access_token": access_token}), 200


@app.route("/submit-preferences", methods=["POST"])
@jwt_required()
def submit_preferences():
    data = request.json
    user_id = get_jwt_identity()  # Get user ID from JWT token

    # Insert into Supabase
    response = supabase.table("user_preferences").insert({
        "user_id": user_id,
        "color": data["color"],
        "fabric": data["fabric"],
        "fit_style": data["fit_style"],
        "personality": data["personality"],
        "accessory": data["accessory"],
        "occasion": data["occasion"],
        "practicality": data["practicality"],
        "comfort_level": data["comfort_level"]
    }).execute()

    return jsonify({"message": "Preferences saved successfully!"})

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True, port=5001)
