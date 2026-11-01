from flask import (
    Flask, render_template, request,
    redirect, url_for, session, jsonify
)
import os
from datetime import date

from dotenv import load_dotenv
from supabase import create_client
from werkzeug.security import check_password_hash


app = Flask(__name__)

# ENVIRONMENT VARIABLES
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Supabase credentials are missing from .env")

if not FLASK_SECRET_KEY:
    raise RuntimeError("FLASK_SECRET_KEY is missing from .env")

app.config["SECRET_KEY"] = FLASK_SECRET_KEY
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# HOSPITAL AND DOCTOR DATA
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

TIME_SLOTS = [
    "09:00",
    "10:00",
    "11:00",
    "12:00",
    "14:00",
    "15:00",
    "16:00"
]


# HOME PAGE
@app.route("/")
def home():
    return render_template("index.html")


# HOSPITALS PAGE
@app.route("/hospitals")
def hospitals_page():
    return render_template("hospitals.html")


# DOCTORS PAGE
@app.route("/doctors")
def doctors_page():

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


# CHECK AVAILABLE APPOINTMENT SLOTS
@app.route("/available-slots")
def available_slots():

    hospital = request.args.get("hospital", "")
    doctor = request.args.get("doctor", "")
    appointment_date = request.args.get("date", "")

    if (
        hospital not in doctors or
        doctor not in doctors.get(hospital, []) or
        not appointment_date
    ):
        return jsonify({
            "error": "Invalid hospital, doctor or date."
        }), 400

    try:
        date.fromisoformat(appointment_date)

        response = (
            supabase.table("appointments")
            .select("appointment_time")
            .eq("hospital", hospital)
            .eq("doctor", doctor)
            .eq("appointment_date", appointment_date)
            .neq("status", "Cancelled")
            .execute()
        )

        booked_slots = [
            appointment["appointment_time"]
            for appointment in response.data
        ]

        return jsonify({
            "booked_slots": booked_slots,
            "available_slots": [
                slot for slot in TIME_SLOTS
                if slot not in booked_slots
            ]
        })

    except ValueError:
        return jsonify({"error": "Invalid appointment date."}), 400

    except Exception as e:
        print("Availability check failed:", e)
        return jsonify({
            "error": "Unable to check appointment availability."
        }), 500


# BOOK APPOINTMENT
@app.route("/book", methods=["GET", "POST"])
def booking():

    if request.method == "POST":

        patient_name = request.form.get(
            "patient_name", ""
        ).strip()

        email = request.form.get(
            "email", ""
        ).strip()

        phone = request.form.get(
            "phone", ""
        ).strip()

        hospital = request.form.get("hospital", "")
        doctor = request.form.get("doctor", "")

        appointment_date = request.form.get(
            "appointment_date", ""
        )

        appointment_time = request.form.get(
            "appointment_time", ""
        )

        appointment_type = request.form.get(
            "appointment_type", "Regular"
        )

        if (
            not patient_name or
            not email or
            not phone or
            len(phone) != 10 or
            not phone.isdigit() or
            hospital not in doctors or
            doctor not in doctors.get(hospital, []) or
            not appointment_date or
            appointment_time not in TIME_SLOTS or
            appointment_type not in ["Regular", "Emergency"]
        ):
            return "Invalid appointment details", 400

        try:
            date.fromisoformat(appointment_date)

        except ValueError:
            return "Invalid appointment date.", 400

        if appointment_date < date.today().isoformat():
            return "Past appointments cannot be booked.", 400

        priority = (
            "High" if appointment_type == "Emergency"
            else "Normal"
        )

        try:

            # CHECK WHETHER THE SLOT IS ALREADY BOOKED
            existing = (
                supabase.table("appointments")
                .select("id")
                .eq("hospital", hospital)
                .eq("doctor", doctor)
                .eq("appointment_date", appointment_date)
                .eq("appointment_time", appointment_time)
                .neq("status", "Cancelled")
                .execute()
            )

            if existing.data:

                return render_template(
                    "booking.html",
                    hospitals=hospitals,
                    doctors=doctors,
                    selected_hospital=hospital,
                    selected_doctor=doctor,
                    error="This time slot is already booked. Please choose another time."
                ), 409

            # INSERT APPOINTMENT
            supabase.table("appointments").insert({

                "patient_name": patient_name,
                "email": email,
                "phone": phone,
                "hospital": hospital,
                "doctor": doctor,
                "appointment_date": appointment_date,
                "appointment_time": appointment_time,
                "appointment_type": appointment_type,
                "priority": priority,
                "status": "Pending"

            }).execute()

            return render_template(
                "booking_success.html",
                patient_name=patient_name,
                hospital=hospital,
                doctor=doctor,
                appointment_date=appointment_date,
                appointment_time=appointment_time
            )

        except Exception as e:

            print("Appointment booking failed:", e)

            return render_template(
                "booking.html",
                hospitals=hospitals,
                doctors=doctors,
                selected_hospital=hospital,
                selected_doctor=doctor,
                error="This appointment slot is unavailable. Please choose another time."
            ), 409

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


# MY APPOINTMENTS
@app.route("/my-appointments", methods=["GET", "POST"])
def my_appointments():

    appointments = []
    searched = False
    email = ""

    if request.method == "POST":

        email = request.form.get("email", "").strip()

        if email:

            try:

                response = (
                    supabase.table("appointments")
                    .select("*")
                    .eq("email", email)
                    .order("created_at", desc=True)
                    .execute()
                )

                appointments = response.data
                searched = True

            except Exception as e:

                print("Error fetching appointments:", e)
                return "Unable to fetch appointments", 500

    return render_template(
        "bookings.html",
        appointments=appointments,
        searched=searched,
        email=email
    )


# CANCEL APPOINTMENT
@app.route("/cancel-appointment/<int:appointment_id>", methods=["POST"])
def cancel_appointment(appointment_id):

    email = request.form.get("email", "").strip()

    if not email:
        return "Registered email is required.", 400

    try:
        response = (
            supabase.table("appointments")
            .update({"status": "Cancelled"})
            .eq("id", appointment_id)
            .eq("email", email)
            .eq("status", "Pending")
            .select()
            .execute()
        )

        if not response.data:
            return """
                <script>
                    alert('No matching Pending appointment found. Check the ID, email and status.');
                    window.location.href = '/my-appointments';
                </script>
            """, 404

        return redirect(url_for("my_appointments"))

    except Exception as e:
        print("CANCELLATION ERROR:", repr(e))
        return "Unable to cancel appointment.", 500


# ADMIN LOGIN
@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():

    if session.get("admin_email"):
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            return render_template(
                "admin_login.html",
                error="Please enter your email and password."
            )

        try:

            response = (
                supabase.table("admin_accounts")
                .select("email, password_hash, hospital")
                .eq("email", email)
                .limit(1)
                .execute()
            )

            admin = response.data[0] if response.data else None

            if (
                admin and
                admin["hospital"] in hospitals and
                check_password_hash(
                    admin["password_hash"], password
                )
            ):

                session.clear()

                session["admin_email"] = admin["email"]
                session["admin_hospital"] = admin["hospital"]

                return redirect(url_for("admin_dashboard"))

            return render_template(
                "admin_login.html",
                error="Invalid email or password."
            )

        except Exception as e:

            print("Admin login error:", e)

            return render_template(
                "admin_login.html",
                error="Unable to log in. Please try again."
            ), 500

    return render_template("admin_login.html")


# ADMIN LOGOUT
@app.route("/admin-logout")
def admin_logout():

    session.clear()

    return redirect(url_for("admin_login"))


# HOSPITAL ADMIN DASHBOARD
@app.route("/admin")
def admin_dashboard():

    if not session.get("admin_email"):
        return redirect(url_for("admin_login"))

    selected_hospital = session.get("admin_hospital")

    if selected_hospital not in hospitals:
        session.clear()
        return redirect(url_for("admin_login"))

    try:

        response = (
            supabase.table("appointments")
            .select("*")
            .eq("hospital", selected_hospital)
            .order("created_at", desc=True)
            .execute()
        )

        appointments = response.data

        # EMERGENCY APPOINTMENTS FIRST
        appointments.sort(
            key=lambda a: (
                0 if a.get("priority") == "High" else 1,
                a.get("created_at", "")
            )
        )

        total = len(appointments)

        pending = sum(
            1 for a in appointments
            if a["status"] == "Pending"
        )

        confirmed = sum(
            1 for a in appointments
            if a["status"] == "Confirmed"
        )

        cancelled = sum(
            1 for a in appointments
            if a["status"] == "Cancelled"
        )

    except Exception as e:

        print("Admin dashboard error:", e)
        return "Unable to load hospital appointments", 500

    return render_template(
        "admin.html",
        hospitals=[selected_hospital],
        selected_hospital=selected_hospital,
        appointments=appointments,
        total=total,
        pending=pending,
        confirmed=confirmed,
        cancelled=cancelled
    )


# CONFIRM APPOINTMENT
@app.route("/confirm-appointment/<int:appointment_id>", methods=["POST"])
def confirm_appointment(appointment_id):

    if not session.get("admin_email"):
        return redirect(url_for("admin_login"))

    selected_hospital = session.get("admin_hospital")

    if selected_hospital not in hospitals:
        session.clear()
        return redirect(url_for("admin_login"))

    try:

        response = (
            supabase.table("appointments")
            .update({"status": "Confirmed"})
            .eq("id", appointment_id)
            .eq("hospital", selected_hospital)
            .eq("status", "Pending")
            .execute()
        )

        if not response.data:
            return "Appointment could not be confirmed.", 409

        return redirect(url_for("admin_dashboard"))

    except Exception as e:

        print("Appointment confirmation failed:", e)
        return "Unable to confirm appointment.", 500


# RUN APPLICATION
if __name__ == "__main__":
    app.run(debug=False)