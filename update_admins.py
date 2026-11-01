import os
from getpass import getpass

from dotenv import load_dotenv
from supabase import create_client
from werkzeug.security import generate_password_hash

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase = create_client(url, key)

print("\n=== MediBook Admin Account Updater ===")

old_email = input("Enter existing admin email: ").strip().lower()
new_email = input("Enter new admin email: ").strip().lower()

new_password = getpass("Enter new password: ")
confirm_password = getpass("Confirm new password: ")

if not new_email or not new_password:
    print("Email and password cannot be empty.")
    exit()

if new_password != confirm_password:
    print("Passwords do not match!")
    exit()

password_hash = generate_password_hash(new_password)

try:
    result = supabase.table("admin_accounts").update({
        "email": new_email,
        "password_hash": password_hash
    }).eq("email", old_email).execute()

    if result.data:
        print("\nAdmin email and password updated successfully!")
    else:
        print("\nNo admin account found with that email.")

except Exception as e:
    print("\nError updating account:", e)