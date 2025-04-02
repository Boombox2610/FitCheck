import os
from supabase import create_client

SUPABASE_URL = "https://chursupvkphjclbiaaky.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNodXJzdXB2a3BoamNsYmlhYWt5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDM1OTIyMTMsImV4cCI6MjA1OTE2ODIxM30.NvZT6GTK-hu7aUkD6l37Wo8jWK6LpdqNQqv2d6M4vg0"


supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def test_login():
    response = supabase.auth.sign_in_with_password({
        "email": "harshmaru2610@gmail.com",
        "password": "12345678"
    })
    print(response)

if __name__ == "__main__":
    test_login()
