from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = "secret123"


# ---------- HOME ----------
@app.route("/")
def welcome():
    return render_template("welcome.html")


@app.route("/home")
def home():
    return render_template("index.html")


@app.route("/select_bus")
def select_bus():
    return render_template("select_bus.html")


# ---------- TRACKING ----------
@app.route("/tracking")
def tracking():
    bus_id = request.args.get("bus", "1")

    buses = {
        "1": {
            "id": "1",
            "name": "Bus 1",
            "route_name": "Main Gate → College",
            "current_stop": "Main Gate",
            "next_stop": "Saraswathipuram",
            "eta": "9 mins",
            "speed": "28 km/h",
        },
        "2": {
            "id": "2",
            "name": "Bus 2",
            "route_name": "City → Campus",
            "current_stop": "City Center",
            "next_stop": "Metro",
            "eta": "6 mins",
            "speed": "24 km/h",
        },
        "3": {
            "id": "3",
            "name": "Bus 3",
            "route_name": "Station → South",
            "current_stop": "Railway Station",
            "next_stop": "Central Park",
            "eta": "5 mins",
            "speed": "26 km/h",
        },
    }

    selected_bus = buses.get(bus_id, buses["1"])

    return render_template(
        "tracking.html",
        bus=selected_bus,
        bus_options=list(buses.values())
    )


# ---------- LOGIN PAGES ----------
@app.route("/student")
def student_login():
    return render_template("login.html", role="student")


@app.route("/parent")
def parent_login():
    return render_template("login.html", role="parent")


@app.route("/driver")
def driver_login():
    return render_template("login.html", role="driver")


@app.route("/admin")
def admin_login():
    return render_template("login.html", role="admin")


# ---------- OTHER PAGES ----------
@app.route("/bus_timing")
def bus_timing():
    return render_template("bus_timing.html")


@app.route("/route_details")
def route_details():
    return render_template("route_details.html")


@app.route("/notifications")
def notifications():
    return render_template("notifications.html")


@app.route("/parent_notifications")
def parent_notifications():
    return render_template("parent_notifications.html")


# ---------- SIMPLE LOGIN (NO DB) ----------
@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    role = request.form.get("role")

    # DEMO USERS
    users = {
        "student": {"username": "disha", "password": "234"},
        "parent": {"username": "parent", "password": "123"},
        "driver": {"username": "driver", "password": "123"},
        "admin": {"username": "admin", "password": "admin"},
    }

    if role in users:
        if username == users[role]["username"] and password == users[role]["password"]:
            session["user"] = {
                "username": username,
                "role": role
            }

            return redirect(f"/{role}_dashboard")

    return "<h2>❌ Invalid Login</h2><a href='/student'>Go Back</a>"


# ---------- DASHBOARDS ----------
@app.route("/student_dashboard")
def student_dashboard():
    if "user" in session:
        return render_template("student.html", user=session["user"])
    return redirect("/student")


@app.route("/parent_dashboard")
def parent_dashboard():
    if "user" in session:
        return render_template("parent.html", user=session["user"])
    return redirect("/parent")


@app.route("/driver_dashboard")
def driver_dashboard():
    if "user" in session:
        return render_template("driver.html", user=session["user"])
    return redirect("/driver")


@app.route("/admin_dashboard")
def admin_dashboard():
    if "user" in session:
        return render_template("admin.html", user=session["user"])
    return redirect("/admin")


# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)