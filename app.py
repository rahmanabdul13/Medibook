from flask import Flask, render_template, request
import os
from dotenv import load_dotenv
from supabase import create_client

app = Flask(__name__)

# Load environment variables
load_dotenv()

# Supabase connection
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/hospitals")
def hospitals():
    return render_template("hospitals.html")


@app.route("/doctors")
def doctors():

    doctor_list = [
        {
            "name": "Dr. Rahul Sharma",
            "specialization": "Cardiologist",
            "hospital": "City Care Hospital",
            "experience": "10 years",
            "icon": "❤️"
        },
        {
            "name": "Dr. Priya Rao",
            "specialization": "General Physician",
            "hospital": "City Care Hospital",
            "experience": "8 years",
            "icon": "🩺"
        },
        {
            "name": "Dr. Ananya Kumar",
            "specialization": "Pediatrician",
            "hospital": "Green Life Hospital",
            "experience": "7 years",
            "icon": "👶"
        },
        {
            "name": "Dr. Vikram Reddy",
            "specialization": "Orthopedic",
            "hospital": "Green Life Hospital",
            "experience": "12 years",
            "icon": "🦴"
        },
        {
            "name": "Dr. Sneha Patel",
            "specialization": "Dermatologist",
            "hospital": "Sunrise Medical Centre",
            "experience": "6 years",
            "icon": "🧴"
        },
        {
            "name": "Dr. Arjun Mehta",
            "specialization": "General Physician",
            "hospital": "Sunrise Medical Centre",
            "experience": "9 years",
            "icon": "🩺"
        }
    ]

    selected_hospital = request.args.get("hospital", "").strip()

    if selected_hospital:
        doctor_list = [
            doctor for doctor in doctor_list
            if doctor["hospital"] == selected_hospital
        ]

    return render_template(
        "doctors.html",
        doctors=doctor_list,
        selected_hospital=selected_hospital
    )


@app.route("/book", methods=["GET", "POST"])
def booking():

    hospitals = [
        "City Care Hospital",
        "Green Life Hospital",
        "Sunrise Medical Centre"
    ]

    doctors = {
        "City Care Hospital": [
            "Dr. Rahul Sharma",
            "Dr. Priya Rao"
        ],
        "Green Life Hospital": [
            "Dr. Ananya Kumar",
            "Dr. Vikram Reddy"
        ],
        "Sunrise Medical Centre": [
            "Dr. Sneha Patel",
            "Dr. Arjun Mehta"
        ]
    }

    if request.method == "POST":

        patient_name = request.form.get("patient_name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        hospital = request.form.get("hospital", "")
        doctor = request.form.get("doctor", "")
        appointment_date = request.form.get("appointment_date", "")
        appointment_time = request.form.get("appointment_time", "")

        if (
            not patient_name or
            not email or
            not phone or
            hospital not in doctors or
            doctor not in doctors.get(hospital, []) or
            not appointment_date or
            not appointment_time
        ):
            return "Invalid appointment details", 400

        return render_template(
            "booking_success.html",
            patient_name=patient_name,
            hospital=hospital,
            doctor=doctor,
            appointment_date=appointment_date,
            appointment_time=appointment_time
        )

    hospital = request.args.get("hospital", "")
    doctor = request.args.get("doctor", "")

    if hospital not in doctors:
        hospital = ""

    if doctor not in doctors.get(hospital, []):
        doctor = ""

    return render_template(
        "booking.html",
        hospitals=hospitals,
        doctors=doctors,
        selected_hospital=hospital,
        selected_doctor=doctor
    )


if __name__ == "__main__":
    app.run(debug=True)