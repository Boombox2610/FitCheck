from flask import Flask, render_template, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from supabase import create_client, Client

from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import base64

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

@app.route("/generate-outfit", methods=["POST"])
@jwt_required()
def generate_outfit():
    user_id = get_jwt_identity()  # Get the logged-in user's ID

    # Fetch user preferences
    preferences = supabase.table("user_preferences").select("*").eq("user_id", user_id).execute().data
    if not preferences:
        return jsonify({"error": "User preferences not found"}), 404

    # Extract preferences
    preferences = preferences[0]
    color = preferences.get("color", "beige")
    fabric = preferences.get("fabric", "cotton")
    fit_style = preferences.get("fit_style", "fit")
    personality = preferences.get("personality", "casual")
    accessory = preferences.get("accessory", "watch")
    occasion = preferences.get("occasion", "casual")
    practicality = "true" if preferences.get("practicality") else "false"
    comfort_level = preferences.get("comfort_level", "high")

    # Construct the prompt string
    contents = (
        f"Here are clothing user preferences: topwear of color {color}, and bottomwear complementing it. "
        f"Fabric: {fabric}. Fit style: {fit_style}. Personality: {personality}. Accessory: {accessory}. "
        f"Occasion: {occasion}. Practical: {practicality}. Comfort level: {comfort_level}. "
        f"Generate only a detailed image prompt for this outfit, from top to bottom, including shoes, which is specific with no ors. "
        f"The prompt should include: clothing be put on a light brown Indian male model with a plain background."
    )

    # Call Gemini API to generate the text prompt
    client = genai.Client(api_key="AIzaSyAD9v7q_nHOrAaHzarJiRGJpiSc8tg13io")
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=contents
    )

    if not response or not response.text:
        print("Failed to generate text prompt")  # Debug log
        return jsonify({"error": "Failed to generate outfit prompt"}), 500

    # Save the generated prompt to the database
    prompt = response.text
    db_response = supabase.table("outfits").insert({
        "user_id": user_id,
        "prompt": prompt,
        "liked": False
    }).execute()

    if db_response.data is None:
        print("Failed to save prompt to database")  # Debug log
        return jsonify({"error": "Failed to save outfit data"}), 500

    # Generate the image based on the prompt
    image_contents = f"Generate only a professional image of {prompt} in a plain background, full body, head to toe."
    print(f"Image generation prompt: {image_contents}")  # Debug log

    image_response = client.models.generate_content(
        model="gemini-2.0-flash-exp-image-generation",
        contents=image_contents,
        config=types.GenerateContentConfig(
            response_modalities=['Text', 'Image']
        )
    )

    if not image_response or not image_response.candidates:
        print("Failed to generate image")  # Debug log
        return jsonify({"error": "Failed to generate outfit image"}), 500

    # Extract the image data
    for part in image_response.candidates[0].content.parts:
        if part.inline_data is not None:
            image_data = part.inline_data.data
            image = Image.open(BytesIO(image_data))
            image_base64 = base64.b64encode(image_data).decode('utf-8')  # Convert image to base64 for frontend display
            print("Image generated successfully")  # Debug log
            break
    else:
        print("No image data found in the response")  # Debug log
        return jsonify({"error": "No image data found"}), 500

    return jsonify({
        "message": "Outfit generated successfully!",
        "prompt": prompt,
        "image": f"data:image/png;base64,{image_base64}",
        "outfit_id": db_response.data[0]["id"]  # Include the outfit ID
    }), 201


@app.route("/update-like-status", methods=["POST"])
@jwt_required()
def update_like_status():
    user_id = get_jwt_identity()  # Get the logged-in user's ID
    data = request.json
    outfit_id = data.get("outfit_id")
    liked = data.get("liked")  # Boolean: true for like, false for dislike

    # Debug logs
    print(f"User ID: {user_id}")
    print(f"Outfit ID: {outfit_id}")
    print(f"Liked: {liked}")

    if outfit_id is None or liked is None:
        return jsonify({"error": "Invalid request data"}), 400

    # Update the `liked` field in the database
    response = supabase.table("outfits").update({"liked": liked}).eq("id", outfit_id).eq("user_id", user_id).execute()

    if response.data is None:
        return jsonify({"error": "Failed to update like status"}), 500

    return jsonify({"message": "Like status updated successfully!"}), 200


@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True, port=5001)
