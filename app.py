import os
import json
import uuid
import hashlib
import traceback
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for
from dotenv import load_dotenv
from ai_generator import generate_strategy
from pdf_generator import generate_pdf_report

load_dotenv()

app = Flask(__name__)
# Use a strong secret key for client-side sessions
app.secret_key = os.environ.get("SECRET_KEY", "coffeestrategy-secure-key-2024-v2")

# Railway/Heroku often have issues with filesystem sessions. 
# Switching to default Flask client-side signed cookie sessions for maximum reliability.
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = 3600 # 1 hour

REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

# Demo payment codes for testing
VALID_PAYMENT_CODES = {"DEMO2024", "COFFEE99", "STRATEGY1"}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/brief")
def brief():
    return render_template("brief.html")

@app.route("/api/generate-preview", methods=["POST"])
def generate_preview():
    """Generate a free preview of the strategy."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Required fields check
        required_fields = ["coffee_name", "location", "target_audience", "coffee_type", "price_range"]
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"Field '{field}' is required"}), 400

        print(f"Generating preview for: {data.get('coffee_name')}")
        strategy = generate_strategy(data, preview_only=True)
        
        # Store in session (Flask will sign this cookie)
        session.permanent = True
        session["brief_data"] = data
        session["strategy_preview"] = strategy
        session["session_id"] = str(uuid.uuid4())
        
        print("Preview generated and stored in session successfully.")
        return jsonify({"success": True, "strategy": strategy})
    except Exception as e:
        print(f"ERROR in /api/generate-preview: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route("/preview")
def preview():
    try:
        strategy = session.get("strategy_preview")
        brief_data = session.get("brief_data")
        
        if not strategy or not brief_data:
            print("Preview accessed without session data. Redirecting to brief.")
            return redirect(url_for("brief"))
            
        return render_template("preview.html", strategy=strategy, brief_data=brief_data)
    except Exception as e:
        print(f"ERROR in /preview route: {str(e)}")
        print(traceback.format_exc())
        return f"Internal Server Error: {str(e)}", 500

@app.route("/payment")
def payment():
    if not session.get("strategy_preview"):
        return redirect(url_for("brief"))
    return render_template("payment.html")

@app.route("/api/process-payment", methods=["POST"])
def process_payment():
    """Process payment and generate full PDF report."""
    try:
        data = request.get_json()
        payment_code = data.get("payment_code", "").strip().upper()
        
        brief_data = session.get("brief_data")
        if not brief_data:
            return jsonify({"error": "Session expired. Please fill the brief again."}), 400

        if payment_code not in VALID_PAYMENT_CODES:
            return jsonify({"error": "Invalid payment code. Use DEMO2024 for testing."}), 400

        # Generate full strategy
        full_strategy = generate_strategy(brief_data, preview_only=False)

        # Generate PDF
        report_id = str(uuid.uuid4())[:8].upper()
        pdf_filename = f"coffee_strategy_{report_id}.pdf"
        pdf_path = os.path.join(REPORTS_DIR, pdf_filename)
        generate_pdf_report(brief_data, full_strategy, pdf_path, report_id)

        session["pdf_filename"] = pdf_filename
        session["report_id"] = report_id

        return jsonify({
            "success": True,
            "report_id": report_id,
            "download_url": f"/download/{pdf_filename}"
        })
    except Exception as e:
        print(f"ERROR in /api/process-payment: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/download/<filename>")
def download_report(filename):
    if not filename.endswith(".pdf") or "/" in filename or ".." in filename:
        return "Invalid file", 400

    pdf_path = os.path.join(REPORTS_DIR, filename)
    if not os.path.exists(pdf_path):
        return "Report not found", 404

    return send_file(pdf_path, as_attachment=True, download_name=filename)

@app.route("/success")
def success():
    report_id = session.get("report_id")
    pdf_filename = session.get("pdf_filename")
    brief_data = session.get("brief_data")
    if not report_id:
        return redirect(url_for("index"))
    return render_template("success.html",
                           report_id=report_id,
                           pdf_filename=pdf_filename,
                           coffee_name=brief_data.get("coffee_name", "") if brief_data else "")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
