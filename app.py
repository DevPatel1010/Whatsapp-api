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
CORS(app, origins=["https://kwezy.framer.website"], supports_credentials=True)         # after you deploy: origins=["https://your-site.com"]

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
    """GET → simple status, POST → forward message to WhatsApp"""
    if request.method == "GET":
        return jsonify(status="WhatsApp endpoint is active",
                       message="Use POST to send messages")
    
    data = request.json or {}
    print("Incoming payload →", data)      # console debug

    name    = data.get("name", "").strip()
    email   = data.get("email", "").strip()
    message = data.get("message", "").strip()

    if not message:
        return jsonify(success=False, message="Message is required"), 400

    # Format exactly like the image example
    body = f"""
📬 New Contact Form Submission

👤 Name: {name or 'Not provided'}
📧 Email: {email or 'Not provided'}
💬 Message: {message} 

"""

    try:
        msg = client.messages.create(
            from_=twilio_from,
            to=whatsapp_to,
            body=body
        )
        return jsonify(success=True, sid=msg.sid)
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

def send_notification(form_data):
    name = form_data.get('name', 'Not provided')
    email = form_data.get('email', 'Not provided')
    message = form_data.get('message', 'Not provided')
    
    # Create a better formatted message template
    notification_template = f"""
📬 New Contact Form Submission

👤 Name: {name}
📧 Email: {email}
💬 Message: {message}

"""
    
    # Send the notification (using your existing method)
    # ...
