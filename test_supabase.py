import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

try:
    supabase = create_client(url, key)

    response = supabase.table("appointments").select("id").limit(1).execute()

    print("Supabase connection successful!")
    print("Appointments table is accessible.")

except Exception as e:
    print("Connection failed!")
    print(e)