import os
from flask import Flask, render_template, request, jsonify
from supabase import create_client

SUPABASE_URL = "https://chursupvkphjclbiaaky.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNodXJzdXB2a3BoamNsYmlhYWt5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDM1OTIyMTMsImV4cCI6MjA1OTE2ODIxM30.NvZT6GTK-hu7aUkD6l37Wo8jWK6LpdqNQqv2d6M4vg0"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__, template_folder="templates", static_folder="static")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/submit-preferences", methods=["POST"])
def submit_preferences():
    data = request.json
    user_id = "f3189819-3866-4040-ad5e-af1ce6964fb3"  # Replace with actual user ID after authentication

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

if __name__ == "__main__":
    app.run(debug=True, port=5001)
