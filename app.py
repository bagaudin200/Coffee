import os
import uuid
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
from ai_generator import generate_strategy
from pdf_generator import generate_pdf_report
from yookassa import Configuration, Payment
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "coffee-secret-2024")

# ЮKassa Configuration
YOOKASSA_SHOP_ID = os.environ.get("YOOKASSA_SHOP_ID")
YOOKASSA_SECRET_KEY = os.environ.get("YOOKASSA_SECRET_KEY")

if YOOKASSA_SHOP_ID and YOOKASSA_SECRET_KEY:
    Configuration.configure(YOOKASSA_SHOP_ID, YOOKASSA_SECRET_KEY)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/brief')
def brief():
    return render_template('brief.html')

@app.route('/api/generate', methods=['POST'])
def api_generate():
    try:
        data = request.json
        session['brief_data'] = data
        
        # Generate preview strategy
        strategy = generate_strategy(data, preview_only=True)
        session['strategy_preview'] = strategy
        
        return jsonify({"success": True, "redirect": url_for('preview')})
    except Exception as e:
        print(f"Error in api_generate: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/preview')
def preview():
    brief_data = session.get('brief_data')
    strategy = session.get('strategy_preview')
    
    if not brief_data or not strategy:
        return redirect(url_for('brief'))
        
    return render_template('preview.html', brief_data=brief_data, strategy=strategy)

@app.route('/payment')
def payment():
    if 'brief_data' not in session:
        return redirect(url_for('brief'))
    return render_template('payment.html')

@app.route('/api/create-payment', methods=['POST'])
def create_payment():
    try:
        email = request.json.get('email')
        if not email:
            return jsonify({"success": False, "error": "Email is required"}), 400
            
        session['user_email'] = email
        
        # Create Yookassa payment
        idempotency_key = str(uuid.uuid4())
        payment_response = Payment.create({
            "amount": {
                "value": "990.00",
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": request.host_url + "success"
            },
            "capture": True,
            "description": f"Маркетинговая стратегия для кофейни ({email})",
            "metadata": {
                "email": email,
                "coffee_name": session.get('brief_data', {}).get('coffee_name', 'Кофейня')
            }
        }, idempotency_key)
        
        # Store payment ID in session to check later
        session['payment_id'] = payment_response.id
        
        return jsonify({
            "success": True, 
            "confirmation_url": payment_response.confirmation.confirmation_url
        })
    except Exception as e:
        print(f"Yookassa Error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/success')
def success():
    # In a real app, we'd check the payment status via API or Webhook
    # For now, we'll assume success if they returned to this URL
    payment_id = session.get('payment_id')
    if not payment_id:
        return redirect(url_for('index'))
        
    return render_template('success.html')

@app.route('/api/download-report')
def download_report():
    try:
        brief_data = session.get('brief_data')
        if not brief_data:
            return "No data found", 404
            
        # Generate full strategy
        full_strategy = generate_strategy(brief_data, preview_only=False)
        
        # Generate PDF
        pdf_path = f"/tmp/strategy_{uuid.uuid4().hex}.pdf"
        generate_pdf_report(brief_data, full_strategy, pdf_path)
        
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"Strategy_{brief_data.get('coffee_name', 'Coffee')}.pdf"
        )
    except Exception as e:
        print(f"PDF Generation Error: {str(e)}")
        return str(e), 500

# Webhook for Yookassa (Optional but recommended for production)
@app.route('/api/yookassa-webhook', methods=['POST'])
def yookassa_webhook():
    # Logic to handle payment.succeeded event
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
