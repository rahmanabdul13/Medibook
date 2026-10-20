from flask import Flask, render_template, request
from flask import Flask, render_template

app = Flask(__name__)


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


@app.route("/book")
def booking():
    return render_template("booking.html")


if __name__ == "__main__":
    app.run(debug=True)