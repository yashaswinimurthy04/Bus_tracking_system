import requests
from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = "secret123"

BACKEND_URL = "http://localhost:5001/api"

# ---------- HOME ----------
@app.route("/")
def welcome():
    bus_count, stop_count = 0, 0 # Default to 0
    try:
        # Fetch all buses from backend
        response = requests.get(f"{BACKEND_URL}/buses")
        if response.status_code == 200:
            buses = response.json()
            bus_count = len(buses)
            
            # Count unique stops
            all_stops = set()
            for bus in buses:
                for stop in bus.get("stops", []):
                    all_stops.add(stop)
            stop_count = len(all_stops)
    except Exception as e:
        print(f"Welcome Fetch Error: {e}")

    return render_template("welcome.html", bus_count=bus_count, stop_count=stop_count)


@app.route("/home")
def home():
    return render_template("index.html")


@app.route("/select_bus")
def select_bus():
    return render_template("select_bus.html")


# ---------- SIGNUP ----------
@app.route("/signup/<role>", methods=["GET", "POST"])
def signup(role):
    if role == "driver":
        return redirect("/driver?msg=Driver registration is managed by admin.")
    if request.method == "POST":
        data = {
            "username": request.form.get("username"),
            "password": request.form.get("password"),
            "role": role,
            "student_name": request.form.get("student_name"),
            "assigned_bus": request.form.get("assigned_bus"),
            "assigned_stop": request.form.get("assigned_stop")
        }
        
        try:
            response = requests.post(f"{BACKEND_URL}/signup", json=data)
            if response.status_code == 201:
                return redirect(f"/{role}?msg=Account created successfully! Please login.")
            else:
                error_msg = response.json().get("message", "Signup failed")
                return render_template("signup.html", role=role, error=error_msg)
        except Exception as e:
            return render_template("signup.html", role=role, error=f"Backend Error: {e}")

    return render_template("signup.html", role=role)


# ---------- TRACKING ----------
@app.route("/tracking")
def tracking():
    bus_id = request.args.get("bus", "1")
    
    try:
        # Fetch detailed bus info
        response = requests.get(f"{BACKEND_URL}/buses/{bus_id}")
        selected_bus = response.json() if response.status_code == 200 else {}

        # Fetch all bus options for the dropdown
        response_all = requests.get(f"{BACKEND_URL}/buses")
        bus_options = response_all.json() if response_all.status_code == 200 else []
    except Exception as e:
        print(f"Error fetching data: {e}")
        selected_bus = {"name": "Offline", "route_name": "N/A", "current_stop": "N/A", "next_stop": "N/A", "eta": "N/A", "speed": "N/A"}
        bus_options = []

    return render_template(
        "tracking.html",
        bus=selected_bus,
        bus_options=bus_options
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


# ---------- API AUTH LOGIN ----------
@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    role = request.form.get("role")

    try:
        response = requests.post(f"{BACKEND_URL}/login", json={
            "username": username,
            "password": password,
            "role": role,
            "bus_id": request.form.get("bus_id")
        })

        if response.status_code == 200:
            user_data = response.json().get("user")
            session["user"] = user_data
            return redirect(f"/{role}_dashboard")
        elif response.status_code == 403: # Pending Approval
            # Admin Bypass: Admins do not need approval
            user_data = response.json().get("user")
            if role == "admin" and user_data:
                session["user"] = user_data
                return redirect("/admin_dashboard")
            return render_template("pending.html", role=role)
        else:
            message = response.json().get("message", "Invalid Login")
            return f"<h2>❌ {message}</h2><a href='/{role}'>Go Back</a>"
    except Exception as e:
        return render_template("pending.html", error=str(e), role=role) # Fallback


# ---------- DASHBOARDS ----------
@app.route("/student_dashboard")
def student_dashboard():
    if "user" in session and session["user"]["role"] == "student":
        return render_template("student.html", user=session["user"])
    return redirect("/student")


@app.route("/parent_dashboard")
def parent_dashboard():
    if "user" in session and session["user"]["role"] == "parent":
        return render_template("parent.html", user=session["user"])
    return redirect("/parent")


@app.route("/driver_dashboard")
def driver_dashboard():
    if "user" in session and session["user"]["role"] == "driver":
        bus_id = session["user"].get("assigned_bus")
        students = []
        if bus_id:
            try:
                resp = requests.get(f"{BACKEND_URL}/api/bus/{bus_id}/students")
                if resp.status_code == 200:
                    students = resp.json()
            except:
                pass
        return render_template("driver.html", user=session["user"], students=students)
    return redirect("/driver")


@app.route("/admin_dashboard")
def admin_dashboard():
    if "user" in session and session["user"]["role"] == "admin":
        try:
            # Fetch pending users
            pending_response = requests.get(f"{BACKEND_URL}/admin/pending_users")
            pending_users = pending_response.json() if pending_response.status_code == 200 else []
            
            # Fetch all users (for Box 4)
            all_users_response = requests.get(f"{BACKEND_URL}/admin/all_users")
            all_users = all_users_response.json() if all_users_response.status_code == 200 else []
            
            # Fetch all buses (for Box 2 Map and Box 3)
            bus_response = requests.get(f"{BACKEND_URL}/buses")
            buses = bus_response.json() if bus_response.status_code == 200 else []

            # Fetch notifications
            note_response = requests.get(f"{BACKEND_URL}/notifications")
            notifications = note_response.json() if note_response.status_code == 200 else []
            
            return render_template("admin.html", 
                                 user=session["user"], 
                                 pending_users=pending_users, 
                                 all_users=all_users,
                                 buses=buses,
                                 notifications=notifications)
        except Exception as e:
            return f"<h2>❌ Error fetching admin data</h2><p>{e}</p><a href='/admin_dashboard'>Retry</a>"
    return redirect("/admin")


@app.route("/approve_user/<int:user_id>")
def approve_user(user_id):
    if "user" in session and session["user"]["role"] == "admin":
        try:
            response = requests.post(f"{BACKEND_URL}/admin/approve_user/{user_id}")
            if response.status_code == 200:
                return redirect("/admin_dashboard?msg=User approved successfully")
            else:
                return f"<h2>❌ Approval Failed</h2><p>{response.json().get('message')}</p><a href='/admin_dashboard'>Go Back</a>"
        except Exception as e:
            return f"<h2>❌ Connection Error</h2><p>{e}</p><a href='/admin_dashboard'>Go Back</a>"
    return redirect("/admin")

@app.route("/delete_user/<int:user_id>")
def delete_user(user_id):
    if "user" in session and session["user"]["role"] == "admin":
        try:
            response = requests.delete(f"{BACKEND_URL}/admin/delete_user/{user_id}")
            if response.status_code == 200:
                return redirect("/admin_dashboard?msg=User removed successfully")
            else:
                return f"<h2>❌ Removal Failed</h2><p>{response.json().get('message')}</p><a href='/admin_dashboard'>Go Back</a>"
        except Exception as e:
            return f"<h2>❌ Connection Error</h2><p>{e}</p><a href='/admin_dashboard'>Go Back</a>"
    return redirect("/admin")

@app.route("/add_bus", methods=["POST"])
def add_bus():
    if "user" in session and session["user"]["role"] == "admin":
        # Collect dynamically added stops from the form
        stops = request.form.getlist("stops[]")
        
        data = {
            "id": request.form.get("id"),
            "route_name": f"{request.form.get('route_from')} → {request.form.get('route_to')}",
            "stops": stops,
            "driver_name": request.form.get("driver_name"),
            # Placeholder defaults for removed fields
            "name": f"Bus {request.form.get('id')}",
            "lat": 12.9716, 
            "lng": 77.5946
        }
        
        try:
            response = requests.post(f"{BACKEND_URL}/admin/add_bus", json=data)
            if response.status_code == 200:
                return redirect("/admin_dashboard?msg=Bus and stops added successfully")
            else:
                return f"<h2>❌ Error</h2><p>{response.json().get('message')}</p><a href='/admin_dashboard'>Go Back</a>"
        except Exception as e:
            return f"<h2>❌ Connection Error</h2><p>{e}</p><a href='/admin_dashboard'>Go Back</a>"
            
    return redirect("/admin")

@app.route("/send_notification", methods=["POST"])
def send_notification():
    if "user" in session and session["user"]["role"] == "admin":
        msg = request.form.get("message")
        requests.post(f"{BACKEND_URL}/notifications", json={"message": msg, "sender": "admin"})
        return redirect("/admin_dashboard?msg=Notification sent")
    return redirect("/admin")


# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ---------- RUN ----------
if __name__ == "__main__":
    app.run(port=5000, debug=True)