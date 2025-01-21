from flask import Flask, request, render_template, send_from_directory
from threading import Thread
import socket
import json
import os
from datetime import datetime

# Flask app setup
app = Flask(__name__, static_folder="static", template_folder="templates")

# Ensure storage directory exists
if not os.path.exists("storage"):
    os.makedirs("storage")
if not os.path.exists("storage/data.json"):
    with open("storage/data.json", "w") as f:
        json.dump({}, f)

# Routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/message.html")
def message():
    return render_template("message.html")

@app.route("/style.css")
def style():
    return send_from_directory(".", "style.css")

@app.route("/logo.png")
def logo():
    return send_from_directory(".", "logo.png")

@app.route("/message", methods=["POST"])
def handle_message():
    username = request.form.get("username")
    message = request.form.get("message")

    if username and message:
        data = {
            "username": username,
            "message": message
        }

        # Send data to socket server
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(json.dumps(data).encode("utf-8"), ("127.0.0.1", 5000))

        return "<h1>Message sent successfully!</h1><a href='/'>Go back</a>"

    return "<h1>Missing username or message!</h1><a href='/message.html'>Try again</a>", 400

@app.errorhandler(404)
def page_not_found(e):
    return render_template("error.html"), 404

# Socket server
def socket_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1", 5000))

    while True:
        data, _ = sock.recvfrom(4096)
        if data:
            message_data = json.loads(data.decode("utf-8"))
            timestamp = str(datetime.now())

            # Save to JSON file
            with open("storage/data.json", "r+") as f:
                existing_data = json.load(f)
                existing_data[timestamp] = message_data
                f.seek(0)
                json.dump(existing_data, f, indent=2)

# Run both servers
if __name__ == "__main__":
    # Start socket server in a separate thread
    socket_thread = Thread(target=socket_server, daemon=True)
    socket_thread.start()

    # Run Flask app
    app.run(host="0.0.0.0", port=3000)
