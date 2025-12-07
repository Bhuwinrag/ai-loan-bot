import os
import re
import random
import sqlite3
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from fpdf import FPDF
from werkzeug.utils import secure_filename

# --- 1. SETUP THE FLASK APP ---
app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists("letters"):
    os.makedirs("letters")

# --- 2. DATABASE SETUP (SQLite) ---
DB_NAME = "loans.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Create users table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            session_id TEXT PRIMARY KEY,
            name TEXT,
            phone TEXT,
            credit_score INTEGER,
            pre_approved_limit INTEGER,
            requested_amount INTEGER,
            tenure_months INTEGER,
            state TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# --- 3. DYNAMIC DATA HELPERS ---
def create_user_profile(session_id, name):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Generate dynamic data
    # Simulate credit score between 600 and 850
    credit_score = random.randint(600, 850)
    
    # Simulate limit based on score
    if credit_score > 750:
        limit = random.choice([100000, 150000, 200000, 250000, 500000])
    elif credit_score > 650:
        limit = random.choice([50000, 60000, 75000, 80000, 100000])
    else:
        limit = random.choice([20000, 30000, 40000])

    # Generate a random phone number for verification simulation
    phone = f"9{random.randint(100000000, 999999999)}"

    cursor.execute('''
        INSERT OR REPLACE INTO users (session_id, name, phone, credit_score, pre_approved_limit, state)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (session_id, name, phone, credit_score, limit, "NEEDS_ANALYSIS"))
    
    conn.commit()
    conn.close()
    return {"name": name, "phone": phone, "credit_score": credit_score, "pre_approved_limit": limit}

def get_user(session_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE session_id = ?', (session_id,)).fetchone()
    conn.close()
    return user

def update_user_state(session_id, state):
    conn = get_db_connection()
    conn.execute('UPDATE users SET state = ? WHERE session_id = ?', (state, session_id))
    conn.commit()
    conn.close()

def update_loan_details(session_id, amount, tenure):
    conn = get_db_connection()
    conn.execute('UPDATE users SET requested_amount = ?, tenure_months = ? WHERE session_id = ?', (amount, tenure, session_id))
    conn.commit()
    conn.close()

# --- 4. WORKER AI AGENTS ---

def worker_sales_agent(user):
    print(f"[Sales Agent] Crafting persuasive greeting for {user['name']}")
    name = user['name'].split(" ")[0]
    limit = user['pre_approved_limit']
    message = (
        f"Hi {name}! I'm your digital sales assistant from Tata Capital. "
        f"Great news! Because you're a valued customer, I see you have a pre-approved personal loan offer of up to Rs. {limit:,}! " 
        "This could be perfect for a home renovation, a vacation, or anything else you need. "
        "Are you interested in discussing this offer today?"
    )
    return {"message": message}

def worker_negotiation_agent(message):
    if any(keyword in message.lower() for keyword in ["interest", "rate", "negotiate", "cheaper"]):
        print("[Sales Agent] Handling negotiation query.")
        return (
            "That's a great question. The interest rate is determined by our underwriting system based on your full credit profile "
            "after you apply. I can assure you that we will provide the best possible rate we can. "
            "To see your final rate, we just need to confirm the amount you need. How much were you thinking of?"
        )
    return None

def worker_verification_agent(user, phone_from_chat):
    print(f"[Verification Agent] Checking {user['name']} with phone {phone_from_chat}")
    # In a real app, we'd check against the DB. Here, we check against the generated phone
    # OR, for better UX in this demo, we can just accept ANY valid 10-digit number as "verified" 
    # since the user doesn't know the random number we generated.
    # BUT, to keep the "simulation" logic intact, let's just say we verify if it's a valid 10 digit number.
    
    if re.match(r'^\d{10}$', phone_from_chat):
        print("[Verification Agent] SUCCESS (Format Valid)")
        return {"status": "verified"}
    
    print("[Verification Agent] FAILED")
    return {"status": "verification_failed"}

def worker_underwriting_agent(user, salary_slip_salary=None):
    requested_amount = user['requested_amount']
    score = user['credit_score']
    limit = user['pre_approved_limit']
    
    print(f"[Underwriting Agent] Evaluating {user['name']} for {requested_amount}")

    if score < 700:
        return {"status": "rejected", "reason": f"Your credit score is {score}, which is below our minimum requirement of 700."}
    if requested_amount > (2 * limit):
        return {"status": "rejected", "reason": f"The requested amount of Rs. {requested_amount:,} is more than double your pre-approved limit of Rs. {limit:,}."}
    if requested_amount <= limit:
        return {"status": "approved_instantly"}
    if requested_amount <= (2 * limit):
        if not salary_slip_salary:
            return {"status": "needs_salary_slip"}
        else:
            total_interest = requested_amount * 0.12 * 2
            total_payable = requested_amount + total_interest
            monthly_emi = total_payable / 24
            if monthly_emi <= (0.5 * salary_slip_salary):
                return {"status": "approved_with_salary"}
            else:
                return {"status": "rejected", "reason": f"Your monthly income of Rs. {salary_slip_salary:,} is not sufficient for an EMI of Rs. {monthly_emi:,.0f}."}
    return {"status": "rejected", "reason": "We are unable to process your loan at this time."}

# Worker Agent 5: Sanction Letter Agent
def worker_sanction_letter_agent(user):
    print(f"[Sanction Letter Agent] Generating PDF for {user['name']}")
    try:
        customer_name = user['name']
        amount = user['requested_amount']
        tenure_months = user['tenure_months']
        interest_rate = random.uniform(11.5, 14.5)
        
        loan_amount_str = f"Rs. {amount:,.0f}"

        pdf = FPDF()
        pdf.add_page()
        
        pdf.set_font("Helvetica", 'B', 16)
        pdf.cell(0, 10, 'Personal Loan Sanction Letter', 0, 1, 'C')
        pdf.set_font("Helvetica", '', 12)

        pdf.ln(10)
        pdf.cell(0, 10, f"Dear {customer_name},", 0, 1)
        pdf.ln(5)
        pdf.multi_cell(0, 7, f"We are pleased to inform you that your personal loan of {loan_amount_str} has been sanctioned.")
        pdf.ln(5)
        
        pdf.cell(0, 7, f"Loan Amount: {loan_amount_str}", 0, 1)
        pdf.cell(0, 7, f"Loan Tenure: {tenure_months} months", 0, 1)
        pdf.cell(0, 7, f"Interest Rate: {interest_rate:.2f}% p.a.", 0, 1)
        pdf.ln(10)
        
        pdf.cell(0, 10, "This is an automated letter and does not require a signature.", 0, 1, 'C')
        
        filename = f"letter_{user['session_id']}.pdf"
        filepath = os.path.join("letters", filename)
        pdf.output(filepath) 
        
        print(f"[Sanction Letter Agent] PDF saved to {filepath}")
        return {"status": "generated", "file_path": f"/letters/{filename}"}
    
    except Exception as e:
        print(f"[Sanction Letter Agent] FAILED: {e}")
        return {"status": "failed"}

# --- 5. THE MASTER AI AGENT ---

@app.route("/")
def index():
    return send_from_directory('.', 'index.html')

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    if not data: return jsonify({"response_message": "Error: No JSON data received."}), 400
    
    message = data.get("message")
    session_id = data.get("session_id") # Changed from customer_id
    metadata = data.get("metadata", {}) # Get metadata if available
    
    if not message or not session_id: return jsonify({"response_message": "Error: 'message' or 'session_id' missing."}), 400
    
    user = get_user(session_id)
    
    # --- NEW: CAMPAIGN / URL PARAMETER HANDLING ---
    if not user and metadata.get("name"):
        # If user doesn't exist but we have a name from URL, create profile immediately
        name = metadata.get("name")
        create_user_profile(session_id, name)
        
        # If amount is also provided, store it
        if metadata.get("amount"):
             conn = get_db_connection()
             conn.execute("UPDATE users SET requested_amount = ? WHERE session_id = ?", (metadata.get("amount"), session_id))
             conn.commit()
             conn.close()
             
        # Skip GREETING, go straight to OFFER (NEEDS_ANALYSIS)
        user = get_user(session_id) # Reload user
        
        # Generate personalized offer immediately
        response_message = (
            f"Welcome back, {user['name']}! We have a special pre-approved offer for you.\n"
            f"You are eligible for a personal loan of up to Rs. {user['pre_approved_limit']:,}!\n"
            "Are you interested in proceeding with this offer?"
        )
        # Update state to NEEDS_ANALYSIS so next message is treated as response to offer
        update_user_state(session_id, "NEEDS_ANALYSIS")
        
        return jsonify({"response_message": response_message})

    # --- NEW: ASK FOR NAME FLOW ---
    if not user:
        # If user doesn't exist, this is the first interaction (or restart)
        # We expect the message to be their name if we are in the "ASK_NAME" phase, 
        # but actually, the frontend will likely send "__START__" first.
        
        if message == "__START__":
             # Just return a prompt for the name. We don't create the user yet.
             return jsonify({"response_message": "Hello! Welcome to Tata Capital. May I know your name?"})
        else:
            # Assume the message IS the name
            name = message.strip()
            if len(name) < 2:
                 return jsonify({"response_message": "Please enter a valid name."})
            
            # Create the user profile dynamically
            user_data = create_user_profile(session_id, name)
            
            # Now generate the sales greeting
            sales_response = worker_sales_agent(user_data)
            return jsonify({"response_message": sales_response["message"]})

    # User exists, proceed with state machine
    state = user['state']
    response_message = ""
    
    if state == "NEEDS_ANALYSIS":
        if any(word in message.lower() for word in ["no", "not", "later"]):
            response_message = "No problem at all! We're here if you change your mind. Have a great day!"
            update_user_state(session_id, "ENDED")
        else:
            # Check if numbers provided
            numbers = [int(s) for s in re.findall(r'\d+', message.replace(',', ''))]
            if len(numbers) >= 2:
                amount = max(numbers)
                tenure = min(numbers)
                update_loan_details(session_id, amount, tenure)
                response_message = f"Got it. You're looking for Rs. {amount:,} for {tenure} months. Before we proceed, I need to verify your identity. Can you please confirm your 10-digit mobile number?"
                update_user_state(session_id, "VERIFICATION")
            elif len(numbers) == 1:
                amount = numbers[0]
                # Update only amount
                conn = get_db_connection()
                conn.execute('UPDATE users SET requested_amount = ? WHERE session_id = ?', (amount, session_id))
                conn.commit()
                conn.close()
                response_message = f"Got it, Rs. {amount:,}. And for how many months would you like to take this loan?"
                update_user_state(session_id, "AWAITING_TENURE")
            else:
                response_message = "That's great! To find the best offer for you, how much money do you need, and for how many months? (e.g., '50000 for 12 months')"
                update_user_state(session_id, "NEEDS_ANALYSIS_AWAITING_REPLY")
            
    elif state == "NEEDS_ANALYSIS_AWAITING_REPLY":
        negotiation_response = worker_negotiation_agent(message)
        if negotiation_response:
            response_message = negotiation_response
        else:
            numbers = [int(s) for s in re.findall(r'\d+', message.replace(',', ''))]
            if len(numbers) >= 2:
                amount = max(numbers)
                tenure = min(numbers)
                update_loan_details(session_id, amount, tenure)
                response_message = f"Got it. You're looking for Rs. {amount:,} for {tenure} months. Before we proceed, I need to verify your identity. Can you please confirm your 10-digit mobile number?"
                update_user_state(session_id, "VERIFICATION")
            elif len(numbers) == 1:
                amount = numbers[0]
                conn = get_db_connection()
                conn.execute('UPDATE users SET requested_amount = ? WHERE session_id = ?', (amount, session_id))
                conn.commit()
                conn.close()
                response_message = f"Got it, Rs. {amount:,}. And for how many months?"
                update_user_state(session_id, "AWAITING_TENURE")
            else:
                response_message = "I'm sorry, I didn't quite catch that. Could you please tell me the loan amount and the tenure in months? For example: 'I need 100000 for 24 months'."

    elif state == "AWAITING_TENURE":
        numbers = [int(s) for s in re.findall(r'\d+', message.replace(',', ''))]
        if numbers:
            tenure = numbers[0]
            # Update tenure
            conn = get_db_connection()
            conn.execute('UPDATE users SET tenure_months = ? WHERE session_id = ?', (tenure, session_id))
            conn.commit()
            conn.close()
            
            # We need to get the amount to confirm
            user = get_user(session_id)
            amount = user['requested_amount']
            
            response_message = f"Understood. Rs. {amount:,} for {tenure} months. To proceed, I need to verify your identity. Can you please confirm your 10-digit mobile number?"
            update_user_state(session_id, "VERIFICATION")
        else:
            response_message = "I didn't catch the duration. Could you please tell me the number of months? (e.g., '12' or '24')"

    elif state == "VERIFICATION":
        phone_from_chat = re.sub(r'\D', '', message)
        verification_result = worker_verification_agent(user, phone_from_chat)
        if verification_result["status"] == "verified":
            response_message = "Thank you, you're verified! Please wait just a moment while I run your details through our underwriting system."
            return run_underwriting(session_id) 
        else:
            response_message = "I'm sorry, that phone number doesn't look right. Please enter a valid 10-digit mobile number."

    elif state == "AWAITING_SALARY_SLIP":
        response_message = "Please use the upload button to submit your salary slip. If you're having trouble, please let me know."

    else: # ENDED
        response_message = "I have already processed your request. Is there anything else I can help you with today?"
    
    return jsonify({"response_message": response_message})

def run_underwriting(session_id, salary=None):
    user = get_user(session_id)
    eval_result = worker_underwriting_agent(user, salary)
    
    status = eval_result["status"]
    response_data = {}
    
    if status == "approved_instantly" or status == "approved_with_salary":
        response_message = f"🎉 Congratulations, {user['name'].split(' ')[0]}! Your loan for Rs. {user['requested_amount']:,} has been approved!"
        letter_result = worker_sanction_letter_agent(user)
        
        if letter_result["status"] == "generated":
            response_message += f" I have generated your sanction letter. You can download it here: {letter_result['file_path']}"
        else:
            response_message += " I was unable to generate your sanction letter at this time, but a copy will be emailed to you."
            
        update_user_state(session_id, "ENDED")
        response_data = {"response_message": response_message}
        
    elif status == "needs_salary_slip":
        response_message = (
            f"You're almost there! Your loan of Rs. {user['requested_amount']:,} is just above your pre-approved limit. "
            "To complete the approval, please upload your latest salary slip using the upload button that just appeared."
        )
        update_user_state(session_id, "AWAITING_SALARY_SLIP")
        response_data = {"response_message": response_message, "action": "show_upload_button"}
        
    elif status == "rejected":
        response_message = f"I'm sorry, {user['name'].split(' ')[0]}. After a review, we are unable to approve your loan at this time. Reason: {eval_result['reason']}"
        update_user_state(session_id, "ENDED")
        response_data = {"response_message": response_message}

    return jsonify(response_data)

# --- 6. FILE UPLOAD ENDPOINT ---
@app.route("/api/upload_salary_slip", methods=["POST"])
def upload_salary_slip():
    try:
        if 'session_id' not in request.form:
             return jsonify({"response_message": "Error: Missing session_id."}), 400
        session_id = request.form['session_id']
        
        if 'salary_slip' not in request.files:
            return jsonify({"response_message": "No file part in the request."}), 400
        file = request.files['salary_slip']
        
        if file.filename == '':
            return jsonify({"response_message": "No file selected."}), 400
        
        filename = secure_filename(f"{session_id}_{file.filename}")
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        print(f"[Master Agent] Received salary slip {filename} for {session_id}")
        
        simulated_salary = random.randint(40000, 120000)
        print(f"[Master Agent] Simulated salary from PDF is: {simulated_salary}")
        
        return run_underwriting(session_id, simulated_salary)

    except Exception as e:
        print(f"[Upload Error] {e}")
        return jsonify({"response_message": "An internal error occurred."}), 500

# --- 7. PDF DOWNLOAD ENDPOINT ---
@app.route("/letters/<filename>", methods=["GET"])
def get_letter(filename):
    try:
        return send_from_directory("letters", filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({"error": "File not found."}), 404

# --- 8. RUN THE SERVER ---
if __name__ == "__main__":
    print("Backend server is running on http://127.0.0.1:5000")
    print("New upload folder created at: /uploads")
    app.run(debug=True, port=5000)