"""
Flask → Twilio WhatsApp micro-service
• Local  : python app.py
• Deploy : gunicorn app:app
"""

import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from twilio.rest import Client
from dotenv import load_dotenv

# ── Load .env automatically in local development ─────────────────────
if os.getenv("FLASK_ENV") != "production":
    load_dotenv()              # pulls variables from .env when FLASK_ENV≠production

# ── Flask app & CORS (open now, restrict later) ──────────────────────
app = Flask(__name__)
CORS(app, origins="*")         # after you deploy: origins=["https://your-site.com"]

# ── Twilio client setup ───────────────────────────────────────────────
account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token  = os.environ["TWILIO_AUTH_TOKEN"]
twilio_from = os.environ["TWILIO_FROM"]      # e.g. whatsapp:+14155238886
whatsapp_to = os.environ["WHATSAPP_TO"]      # your phone (E.164) in sandbox
client = Client(account_sid, auth_token)

# ── Routes ────────────────────────────────────────────────────────────
@app.route("/")                          # local browser smoke-test
def index():
    return send_from_directory(".", "index.html")

@app.route("/send-whatsapp", methods=["GET", "POST"])
def send_whatsapp():
    if request.method == "GET":
        return jsonify(status="WhatsApp endpoint is active",
                       message="POST here to send messages")

    data = request.json or {}
    name    = data.get("name", "").strip()
    email   = data.get("email", "").strip()
    message = data.get("message", "").strip()

    if not message:
        return jsonify(success=False, message="Message is required"), 400

    body_parts = []
    if name:
        body_parts.append(f"From: {name}")
    body_parts.append(message)
    if email:
        body_parts.append(f"Contact: {email}")
    body = "\n".join(body_parts)

    try:
        twilio_msg = client.messages.create(
            from_=twilio_from,
            to=whatsapp_to,
            body=body
        )
        return jsonify(success=True, sid=twilio_msg.sid)
    except Exception as exc:
        print("Twilio error →", exc)
        return jsonify(success=False, message=str(exc)), 500

@app.route("/health")
def health():
    return jsonify(status="ok")

# ── Local dev entrypoint ─────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"🚀  Running on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
