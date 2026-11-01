import os
from getpass import getpass

from dotenv import load_dotenv
from supabase import create_client
from werkzeug.security import generate_password_hash

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase = create_client(url, key)

hospitals = [
    "City Care Hospital",
    "Green Life Hospital",
    "Sunrise Medical Centre"
]

for hospital in hospitals:
    print(f"\n--- Create Admin: {hospital} ---")

    email = input("Enter admin email: ").strip().lower()
    password = getpass("Enter admin password: ")

    if not email or not password:
        print("Email and password cannot be empty. Skipping.")
        continue

    password_hash = generate_password_hash(password)

    try:
        supabase.table("admin_accounts").insert({
            "email": email,
            "password_hash": password_hash,
            "hospital": hospital
        }).execute()

        print(f"Admin account created for {hospital}!")

    except Exception as e:
        print(f"Could not create account: {e}")

print("\nAdmin account setup completed.")