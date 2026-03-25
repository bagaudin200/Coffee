import os
import json
import uuid
import hashlib
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for
from flask_session import Session
from dotenv import load_dotenv
from ai_generator import generate_strategy
from pdf_generator import generate_pdf_report

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "coffeestrategy-secret-2024")
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_FILE_DIR"] = "/tmp/flask_sessions"
app.config["SESSION_PERMANENT"] = False
os.makedirs("/tmp/flask_sessions", exist_ok=True)
Session(app)

REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

# Demo payment codes for testing (in production use Stripe)
VALID_PAYMENT_CODES = {"DEMO2024", "COFFEE99", "STRATEGY1"}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/brief")
def brief():
    return render_template("brief.html")


@app.route("/api/generate-preview", methods=["POST"])
def generate_preview():
    """Generate a free preview of the strategy (limited version)."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    required_fields = ["coffee_name", "location", "target_audience", "coffee_type", "price_range"]
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"Field '{field}' is required"}), 400

    try:
        strategy = generate_strategy(data, preview_only=True)
        # Store full brief in session for later PDF generation
        session["brief_data"] = data
        session["strategy_preview"] = strategy
        session_id = str(uuid.uuid4())
        session["session_id"] = session_id
        return jsonify({"success": True, "strategy": strategy, "session_id": session_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/preview")
def preview():
    strategy = session.get("strategy_preview")
    brief_data = session.get("brief_data")
    if not strategy or not brief_data:
        return redirect(url_for("brief"))
    return render_template("preview.html", strategy=strategy, brief_data=brief_data)


@app.route("/payment")
def payment():
    strategy = session.get("strategy_preview")
    if not strategy:
        return redirect(url_for("brief"))
    return render_template("payment.html")


@app.route("/api/process-payment", methods=["POST"])
def process_payment():
    """Process payment and generate full PDF report."""
    data = request.get_json()
    payment_code = data.get("payment_code", "").strip().upper()
    email = data.get("email", "").strip()

    brief_data = session.get("brief_data")
    if not brief_data:
        return jsonify({"error": "Session expired. Please fill the brief again."}), 400

    # Check payment code (demo mode)
    if payment_code not in VALID_PAYMENT_CODES:
        return jsonify({"error": "Invalid payment code. Use DEMO2024 for testing."}), 400

    try:
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
        return jsonify({"error": str(e)}), 500


@app.route("/download/<filename>")
def download_report(filename):
    """Download the generated PDF report."""
    # Security: only allow files from reports directory
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


@app.route("/api/stripe-checkout", methods=["POST"])
def stripe_checkout():
    """Create Stripe checkout session (requires Stripe keys)."""
    import stripe
    stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

    if not stripe.api_key:
        return jsonify({"error": "Stripe not configured. Use demo payment code DEMO2024"}), 400

    data = request.get_json()
    brief_data = session.get("brief_data")
    if not brief_data:
        return jsonify({"error": "Session expired"}), 400

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": "Coffee Strategy PDF Report",
                        "description": f"Full marketing strategy for {brief_data.get('coffee_name', 'your coffee shop')}",
                    },
                    "unit_amount": 2900,  # $29.00
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=request.host_url + "stripe-success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=request.host_url + "payment",
        )
        return jsonify({"checkout_url": checkout_session.url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/stripe-success")
def stripe_success():
    """Handle successful Stripe payment."""
    import stripe
    stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
    checkout_session_id = request.args.get("session_id")

    brief_data = session.get("brief_data")
    if not brief_data or not checkout_session_id:
        return redirect(url_for("index"))

    try:
        checkout_session = stripe.checkout.Session.retrieve(checkout_session_id)
        if checkout_session.payment_status == "paid":
            full_strategy = generate_strategy(brief_data, preview_only=False)
            report_id = str(uuid.uuid4())[:8].upper()
            pdf_filename = f"coffee_strategy_{report_id}.pdf"
            pdf_path = os.path.join(REPORTS_DIR, pdf_filename)
            generate_pdf_report(brief_data, full_strategy, pdf_path, report_id)
            session["pdf_filename"] = pdf_filename
            session["report_id"] = report_id
            return redirect(url_for("success"))
    except Exception as e:
        pass

    return redirect(url_for("payment"))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
