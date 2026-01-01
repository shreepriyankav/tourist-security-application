from flask import Flask, render_template, request, redirect, session
import sqlite3
import hashlib
import datetime
import smtplib
from email.message import EmailMessage


EMAIL_ADDRESS = "developshalini112220@gmail.com"
EMAIL_PASSWORD = "cbby rtxd ozjd nfog"
ADMIN_EMAIL = "developshalini112220@gmail.com"


app = Flask(__name__)
app.secret_key = "tourist_safety_secret"

# ---------------- DATABASE ---------------- #
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()

    # Tourist Table
    c.execute("""
    CREATE TABLE IF NOT EXISTS tourists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT,
        phone TEXT,
        emergency_contact TEXT,
        health_info TEXT,
        digital_id TEXT,
        created_at TEXT
    )
    """)

    # Itinerary Table
    c.execute("""
    CREATE TABLE IF NOT EXISTS itineraries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tourist_id INTEGER,
        start_date TEXT,
        end_date TEXT,
        locations TEXT,
        schedule TEXT,
        status TEXT,
        created_at TEXT,
        FOREIGN KEY (tourist_id) REFERENCES tourists(id)
    )
    """)

# Geo-Fence Table
    c.execute("""
    CREATE TABLE IF NOT EXISTS geofences (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        zone_name TEXT,
        zone_type TEXT,
        warning TEXT
    )
    """)
    
    
    # Check-In Table
    c.execute("""
    CREATE TABLE IF NOT EXISTS checkins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tourist_id INTEGER,
        status TEXT,
        message TEXT,
        timestamp TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------------- HOME ---------------- #
@app.route("/")
def home():
    return render_template("home.html")

# ---------------- ADMIN ---------------- #
@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form["username"] == "admin" and request.form["password"] == "admin123":
            session["admin"] = True
            return redirect("/admin/dashboard")
        return "Invalid Admin Credentials"
    return render_template("admin_login.html")

@app.route("/admin/dashboard")
def admin_dashboard():
    if "admin" not in session:
        return redirect("/admin")
    return render_template("admin_dashboard.html")

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect("/")

# ---------------- TOURIST REGISTER ---------------- #
@app.route("/tourist/register", methods=["GET", "POST"])
def tourist_register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        emergency = request.form["emergency"]
        health = request.form["health"]
        password = hashlib.sha256(request.form["password"].encode()).hexdigest()

        timestamp = str(datetime.datetime.now())
        digital_id = hashlib.sha256((email + timestamp).encode()).hexdigest()

        conn = get_db()
        c = conn.cursor()
        try:
            c.execute("""
                INSERT INTO tourists 
                (name, email, password, phone, emergency_contact, health_info, digital_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, email, password, phone, emergency, health, digital_id, timestamp))
            conn.commit()
            return redirect("/tourist/login")
        except:
            return "User already exists"

    return render_template("tourist_register.html")

# ---------------- TOURIST LOGIN ---------------- #
@app.route("/tourist/login", methods=["GET", "POST"])
def tourist_login():
    if request.method == "POST":
        email = request.form["email"]
        password = hashlib.sha256(request.form["password"].encode()).hexdigest()

        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT * FROM tourists WHERE email=? AND password=?", (email, password))
        user = c.fetchone()

        if user:
            session["tourist"] = user["id"]
            return redirect("/tourist/dashboard")
        return "Invalid Login"

    return render_template("tourist_login.html")

# ---------------- TOURIST DASHBOARD ---------------- #
@app.route("/tourist/dashboard")
def tourist_dashboard():
    if "tourist" not in session:
        return redirect("/tourist/login")
    return render_template("tourist_dashboard.html")

# ---------------- CREATE ITINERARY ---------------- #
@app.route("/tourist/itinerary/new", methods=["GET", "POST"])
def create_itinerary():
    if "tourist" not in session:
        return redirect("/tourist/login")

    if request.method == "POST":
        start = request.form["start_date"]
        end = request.form["end_date"]
        locations = request.form["locations"]
        schedule = request.form["schedule"]

        conn = get_db()
        c = conn.cursor()
        c.execute("""
            INSERT INTO itineraries 
            (tourist_id, start_date, end_date, locations, schedule, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            session["tourist"],
            start,
            end,
            locations,
            schedule,
            "Active",
            str(datetime.datetime.now())
        ))
        conn.commit()
        return redirect("/tourist/itineraries")

    return render_template("create_itinerary.html")

# ---------------- VIEW ITINERARIES ---------------- #
@app.route("/tourist/itineraries")
def view_itineraries():
    if "tourist" not in session:
        return redirect("/tourist/login")

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM itineraries WHERE tourist_id=?", (session["tourist"],))
    trips = c.fetchall()

    return render_template("view_itineraries.html", trips=trips)

# ---------------- CANCEL ITINERARY ---------------- #
@app.route("/tourist/itinerary/cancel/<int:id>")
def cancel_itinerary(id):
    if "tourist" not in session:
        return redirect("/tourist/login")

    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE itineraries SET status='Cancelled' WHERE id=?", (id,))
    conn.commit()

    return redirect("/tourist/itineraries")

# ---------------- DIGITAL ID ---------------- #
@app.route("/tourist/digital-id")
def digital_id():
    if "tourist" not in session:
        return redirect("/tourist/login")

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM tourists WHERE id=?", (session["tourist"],))
    user = c.fetchone()

    return render_template("digital_id.html", user=user)


@app.route("/tourist/geofence", methods=["GET", "POST"])
def geofence_awareness():
    if "tourist" not in session:
        return redirect("/tourist/login")

    conn = get_db()
    c = conn.cursor()

    alert = ""  # Initialize alert flag

    if request.method == "POST":
        zone_id = request.form["zone_id"]

        c.execute("SELECT * FROM geofences WHERE id=?", (zone_id,))
        zone = c.fetchone()

        # Get tourist details
        c.execute("SELECT * FROM tourists WHERE id=?", (session["tourist"],))
        tourist = c.fetchone()

        # If unsafe zone → send alert
        if zone["zone_type"] in ["Restricted", "Emergency"]:
            subject = "⚠️ Unsafe Zone Alert"
            body = f"""
Dear {tourist['name']},

You have entered or selected an unsafe zone.

Zone Name: {zone['zone_name']}
Zone Type: {zone['zone_type']}
Warning: {zone['warning']}

Please take necessary precautions.

- Smart Tourist Safety System
            """
            send_email_alert(tourist["email"], subject, body)
            send_email_alert(tourist["emergency_contact"], subject, body)
            send_email_alert(ADMIN_EMAIL, subject, body)

            alert = "unsafe"  # Set alert flag
        else:
            alert = "safe"

    c.execute("SELECT * FROM geofences")
    zones = c.fetchall()

    return render_template("geofence.html", zones=zones, alert=alert)


# @app.route("/tourist/geofence")
# def geofence_awareness():
#     if "tourist" not in session:
#         return redirect("/tourist/login")

#     conn = get_db()
#     c = conn.cursor()
#     c.execute("SELECT * FROM geofences")
#     zones = c.fetchall()

#     return render_template("geofence.html", zones=zones)



@app.route("/tourist/checkin", methods=["GET", "POST"])
def checkin():
    if "tourist" not in session:
        return redirect("/tourist/login")

    if request.method == "POST":
        status = request.form["status"]
        message = request.form["message"]

        conn = get_db()
        c = conn.cursor()
        c.execute("""
            INSERT INTO checkins (tourist_id, status, message, timestamp)
            VALUES (?, ?, ?, ?)
        """, (
            session["tourist"],
            status,
            message,
            str(datetime.datetime.now())
        ))
        conn.commit()

        return redirect("/tourist/dashboard")

    return render_template("checkin.html")




@app.route("/tourist/post-trip")
def post_trip_report():
    if "tourist" not in session:
        return redirect("/tourist/login")

    conn = get_db()
    c = conn.cursor()

    # Trips
    c.execute("SELECT COUNT(*) FROM itineraries WHERE tourist_id=?", (session["tourist"],))
    trips = c.fetchone()[0]

    # Check-ins
    c.execute("SELECT COUNT(*) FROM checkins WHERE tourist_id=?", (session["tourist"],))
    checkins = c.fetchone()[0]

    # Emergency count
    c.execute("""
        SELECT COUNT(*) FROM checkins 
        WHERE tourist_id=? AND status='Need Help'
    """, (session["tourist"],))
    emergencies = c.fetchone()[0]

    # Safety Score (simple logic)
    score = max(0, 100 - emergencies * 20)

    return render_template(
        "post_trip.html",
        trips=trips,
        checkins=checkins,
        emergencies=emergencies,
        score=score
    )




@app.route("/admin/tourists")
def admin_tourists():
    if "admin" not in session:
        return redirect("/admin")

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM tourists")
    tourists = c.fetchall()

    return render_template("admin_tourists.html", tourists=tourists)



@app.route("/admin/geofences", methods=["GET", "POST"])
def admin_geofences():
    if "admin" not in session:
        return redirect("/admin")

    conn = get_db()
    c = conn.cursor()

    if request.method == "POST":
        name = request.form["name"]
        ztype = request.form["type"]
        warning = request.form["warning"]

        c.execute("""
            INSERT INTO geofences (zone_name, zone_type, warning)
            VALUES (?, ?, ?)
        """, (name, ztype, warning))
        conn.commit()

    c.execute("SELECT * FROM geofences")
    zones = c.fetchall()

    return render_template("admin_geofences.html", zones=zones)

@app.route("/admin/itineraries")
def admin_itineraries():
    if "admin" not in session:
        return redirect("/admin")

    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT itineraries.*, tourists.name 
        FROM itineraries 
        JOIN tourists ON itineraries.tourist_id = tourists.id
    """)
    trips = c.fetchall()

    return render_template("admin_itineraries.html", trips=trips)


@app.route("/admin/incidents")
def admin_incidents():
    if "admin" not in session:
        return redirect("/admin")

    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT checkins.*, tourists.name 
        FROM checkins 
        JOIN tourists ON checkins.tourist_id = tourists.id
        ORDER BY timestamp DESC
    """)
    incidents = c.fetchall()

    return render_template("admin_incidents.html", incidents=incidents)



@app.route("/admin/blockchain")
def admin_blockchain():
    if "admin" not in session:
        return redirect("/admin")

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT name, digital_id, created_at FROM tourists")
    logs = c.fetchall()

    return render_template("admin_blockchain.html", logs=logs)




def send_email_alert(to_email, subject, body):
    try:
        msg = EmailMessage()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.set_content(body)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)

    except Exception as e:
        print("Email error:", e)













# ---------------- LOGOUT ---------------- #
@app.route("/tourist/logout")
def tourist_logout():
    session.pop("tourist", None)
    return redirect("/")

# ---------------- RUN ---------------- #
if __name__ == "__main__":
    app.run(debug=True)
