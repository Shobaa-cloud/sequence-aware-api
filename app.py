from flask import Flask, request, jsonify
import datetime
import os

app = Flask(__name__)

# -------------------------
# MULTI-USER SESSION STORE
# -------------------------
# user_id -> logged_in (True / False)
user_sessions = {}

# -------------------------
# LOG DIRECTORY SETUP
# -------------------------
LOG_DIR = os.path.join(os.getcwd(), "logs")

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def log_api_call(user, event):
    timestamp = datetime.datetime.now()
    log_file = os.path.join(LOG_DIR, f"{user}.txt")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} - {event}\n")

# -------------------------
# LOGIN API
# -------------------------
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user = data.get("user") if data else None

    if not user:
        return jsonify({"error": "user required"}), 400

    user_sessions[user] = True
    log_api_call(user, "login")

    return jsonify({
        "user": user,
        "status": "logged in"
    })

# -------------------------
# GET DATA (PROTECTED)
# -------------------------
@app.route("/get_data", methods=["POST"])
def get_data():
    data = request.get_json()
    user = data.get("user") if data else None

    if not user:
        return jsonify({"error": "user required"}), 400

    if not user_sessions.get(user, False):
        log_api_call(user, "MISUSE: get_data_before_login")
        return jsonify({"error": "login required"}), 403

    log_api_call(user, "get_data")

    return jsonify({
        "user": user,
        "data": "Here is your data"
    })

# -------------------------
# LOGOUT API
# -------------------------
@app.route("/logout", methods=["POST"])
def logout():
    data = request.get_json()
    user = data.get("user") if data else None

    if not user:
        return jsonify({"error": "user required"}), 400

    if not user_sessions.get(user, False):
        log_api_call(user, "MISUSE: logout_without_login")
        return jsonify({"error": "not logged in"}), 400

    user_sessions[user] = False
    log_api_call(user, "logout")

    return jsonify({
        "user": user,
        "status": "logged out"
    })

# -------------------------
# RUN SERVER (WINDOWS SAFE)
# -------------------------
if __name__ == "__main__":
    print("SERVER STARTED — SEQUENCE-AWARE MULTI-USER MODE 🚀")
     port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)



