from flask import Flask, render_template_string, request, redirect, session, send_file, send_from_directory
import random
from collections import deque
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret123"

heart_history = deque(maxlen=10)
movement_history = deque(maxlen=10)

alert_active = False
alert_time = ""
sms_message = ""
risk_level = "Low"

patients = ["Patient A", "Patient B"]
locations = ["Nairobi", "Embu", "Mombasa"]

# -------- LOGIN PAGE --------
LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Login</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
body { font-family: Arial; background:#0f172a; display:flex; justify-content:center; align-items:center; height:100vh; }
.card { background:white; padding:30px; border-radius:20px; width:300px; text-align:center; }
input { width:90%; padding:10px; margin:10px; border-radius:10px; border:1px solid #ccc; }
button { width:100%; padding:10px; background:#2563eb; color:white; border:none; border-radius:10px; }
</style>
</head>
<body>
<div class="card">
<h2>🔐 Login</h2>
<form method="POST">
<input name="username" placeholder="Username" required>
<input name="password" type="password" placeholder="Password" required>
<button type="submit">Login</button>
</form>
<p style="color:red;">{{error}}</p>
</div>
</body>
</html>
"""

# -------- DASHBOARD --------
DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Healthcare App</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<link rel="manifest" href="/manifest.json">

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<style>
body { margin:0; font-family:Arial; background:#0f172a; color:white; }
.header { background:#1e293b; padding:15px; text-align:center; font-size:18px; }
.container { padding:15px; }

.card {
background:#1e293b;
padding:15px;
border-radius:15px;
margin-bottom:10px;
}

.low { color:#22c55e; }
.medium { color:#facc15; }
.high { color:#ef4444; font-weight:bold; }

button {
width:100%;
padding:10px;
border:none;
border-radius:10px;
background:#ef4444;
color:white;
margin-top:5px;
}

input {
width:95%;
padding:10px;
margin:5px 0;
border-radius:10px;
border:none;
}

.logout {
background:#334155;
}
</style>
</head>

<body>

<div class="header">👵 Smart Healthcare App</div>

<div class="container">

<form method="POST">
<input name="heart" placeholder="Heart Rate">
<input name="move" placeholder="Movement">
<button type="submit">Simulate</button>
</form>

<div class="card"><b>{{patient}}</b><br>📍 {{location}}</div>

<div class="card">❤️ Heart Rate: {{heart}}</div>
<div class="card">🏃 Movement: {{move}}</div>

<div class="card">
Risk: <span class="{{risk_class}}">{{risk}}</span>
</div>

<div class="card">
{% if alert %}
🚨 FALL DETECTED<br>
{{time}}
{% else %}
✅ Normal
{% endif %}
</div>

{% if alert %}
<div class="card">📩 {{sms}}</div>
<div class="card">🚑 Caregiver Notified</div>

<form method="POST" action="/cancel">
<button>I AM OK</button>
</form>
{% endif %}

<div class="card"><b>AI:</b> {{ai}}</div>

<form action="/download">
<button>Download Data</button>
</form>

<form action="/logout">
<button class="logout">Logout</button>
</form>

<canvas id="chart"></canvas>

</div>

<script>
let typing = false;
document.querySelectorAll("input").forEach(input => {
input.addEventListener("focus", () => typing = true);
input.addEventListener("blur", () => typing = false);
});

setInterval(()=>{
if(!typing){ location.reload(); }
},3000);

if ('serviceWorker' in navigator) {
navigator.serviceWorker.register('/service-worker.js');
}

new Chart(document.getElementById('chart'), {
type:'line',
data:{
labels: {{labels}},
datasets:[
{label:'Heart', data:{{heart_data}}},
{label:'Movement', data:{{move_data}}}
]}
});
</script>

</body>
</html>
"""

# -------- ROUTES --------
@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == "admin" and request.form["password"] == "1234":
            session["user"] = "admin"
            return redirect("/dashboard")
        else:
            return render_template_string(LOGIN_HTML, error="Invalid credentials")

    return render_template_string(LOGIN_HTML, error="")


@app.route("/dashboard", methods=["GET","POST"])
def dashboard():
    if "user" not in session:
        return redirect("/")

    global alert_active, alert_time, sms_message, risk_level

    if request.method == "POST":
        try:
            heart = int(request.form["heart"])
            move = int(request.form["move"])
        except:
            heart = random.randint(60,130)
            move = random.randint(0,200)
    else:
        heart = random.randint(60,130)
        move = random.randint(0,200)

    patient = random.choice(patients)
    location = random.choice(locations)

    heart_history.append(heart)
    movement_history.append(move)

    if heart > 120 and move > 150:
        risk_level = "High"
        alert_active = True
        alert_time = datetime.now().strftime("%H:%M:%S")
        sms_message = f"Emergency! Fall detected for {patient} at {location}"

        with open("data_log.txt","a") as f:
            f.write(f"{patient},{location},{heart},{move},{alert_time}\\n")

        ai = "High-risk fall detected using AI sensor fusion."
    elif heart > 100 or move > 80:
        risk_level = "Medium"
        alert_active = False
        ai = "Moderate anomaly detected."
    else:
        risk_level = "Low"
        alert_active = False
        ai = "Normal activity."

    return render_template_string(
        DASHBOARD_HTML,
        heart=heart,
        move=move,
        patient=patient,
        location=location,
        alert=alert_active,
        time=alert_time,
        sms=sms_message,
        risk=risk_level,
        risk_class=risk_level.lower(),
        ai=ai,
        labels=list(range(len(heart_history))),
        heart_data=list(heart_history),
        move_data=list(movement_history)
    )


@app.route("/cancel", methods=["POST"])
def cancel():
    global alert_active
    alert_active = False
    return redirect("/dashboard")


@app.route("/download")
def download():
    return send_file("data_log.txt", as_attachment=True)


@app.route('/manifest.json')
def manifest():
    return send_from_directory('.', 'manifest.json')


@app.route('/service-worker.js')
def sw():
    return send_from_directory('.', 'service-worker.js')


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)