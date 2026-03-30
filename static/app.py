from flask import Flask, request
import random
from datetime import datetime

app = Flask(__name__, static_folder='static')

# GLOBAL STATES
alert_active = False
alert_message = ""
alert_time = ""

@app.route("/", methods=["GET", "POST"])
def home():
    global alert_active, alert_message, alert_time

    if request.method == "POST":
        if "trigger" in request.form:
            alert_active = True
            alert_time = datetime.now().strftime("%H:%M:%S")
            alert_message = "🚨 FALL DETECTED!"
        elif "cancel" in request.form:
            alert_active = False
            alert_message = "✅ Alert Cancelled"

    heart_rate = random.randint(60, 130)
    movement = random.randint(0, 150)

    if movement > 100 and heart_rate > 110:
        alert_active = True
        alert_message = "🚨 FALL DETECTED (AI)"
        alert_time = datetime.now().strftime("%H:%M:%S")

    if alert_active:
        status = f"<h2 style='color:red;'>{alert_message}</h2><p>Time: {alert_time}</p>"
    else:
        status = "<h2 style='color:green;'>✅ Normal Monitoring</h2>"

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>IoT Healthcare</title>

        <!-- FIXED LINKS -->
        <link rel="manifest" href="/static/manifest.json">
        <meta name="theme-color" content="#0f172a">
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

        <style>
            body {{
                font-family: Arial;
                text-align: center;
                background: #0f172a;
                color: white;
            }}
            button {{
                padding: 12px;
                margin: 10px;
                font-size: 16px;
                border-radius: 10px;
                border: none;
            }}
            .trigger {{ background: red; color: white; }}
            .cancel {{ background: green; color: white; }}
        </style>
    </head>

    <body>

        <h1>📱 IoT Healthcare Monitoring</h1>

        {status}

        <p>❤️ Heart Rate: {heart_rate}</p>
        <p>🏃 Movement: {movement}</p>

        <form method="POST">
            <button class="trigger" name="trigger">Trigger Fall</button>
            <button class="cancel" name="cancel">Cancel Alert</button>
        </form>

        <canvas id="chart"></canvas>

        <script>
            const ctx = document.getElementById('chart').getContext('2d');

            new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: ['1','2','3','4','5'],
                    datasets: [
                        {{
                            label: 'Heart Rate',
                            data: [{random.randint(60,130)}, {random.randint(60,130)}, {random.randint(60,130)}, {random.randint(60,130)}, {random.randint(60,130)}],
                            borderWidth: 2
                        }},
                        {{
                            label: 'Movement',
                            data: [{random.randint(0,150)}, {random.randint(0,150)}, {random.randint(0,150)}, {random.randint(0,150)}, {random.randint(0,150)}],
                            borderWidth: 2
                        }}
                    ]
                }}
            }});

            // SERVICE WORKER
            if ('serviceWorker' in navigator) {{
                navigator.serviceWorker.register('/static/service-worker.js')
                .then(() => console.log("Service Worker Registered"));
            }}
        </script>

    </body>
    </html>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)