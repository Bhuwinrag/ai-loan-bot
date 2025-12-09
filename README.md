# Tata Capital AI Loan Bot

This project is an intelligent, automated loan application chatbot designed to assist users in checking their eligibility, negotiating interest rates, and generating sanction letters for personal loans.

##  Features

*   **Intelligent Chat Interface**: A conversational AI that guides users through the loan application process.
*   **Multi-Agent Architecture**:
    *   **Sales Agent**: Engages users with personalized greetings and offers.
    *   **Negotiation Agent**: Handles queries about interest rates and terms.
    *   **Verification Agent**: Simulates mobile number verification.
    *   **Underwriting Agent**: evaluates loan eligibility based on credit score, income, and requested amount.
    *   **Sanction Letter Agent**: Generates a downloadable PDF sanction letter upon approval.
*   **Dynamic Data**: Uses a lightweight SQLite database to manage user profiles, credit scores, and application states.
*   **Campaign Support**: Supports URL parameters for marketing campaigns (e.g., `?name=John&amount=500000`) to pre-fill data and skip initial steps.
*   **Document Upload**: Allows users to upload salary slips for income verification if the loan amount exceeds pre-approved limits.

##  Tech Stack

*   **Backend**: Python (Flask)
*   **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
*   **Database**: SQLite
*   **PDF Generation**: FPDF
*   **Deployment**: Render 

##  Project Structure

*   `app.py`: The core Flask application containing all backend logic, AI agents, and database interactions.
*   `index.html`: The frontend interface handling the chat UI, API communication, and dynamic updates.
*   `loans.db`: SQLite database file (created automatically).
*   `requirements.txt`: List of Python dependencies.
*   `Procfile`: Configuration file for deployment on Render.
*   `uploads/`: Directory for storing uploaded salary slips.
*   `letters/`: Directory for storing generated sanction letters.

##  Getting Started

### Prerequisites

*   Python 3.8+
*   Git

### Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/YOUR_USERNAME/ai-loan-bot.git
    cd ai-loan-bot
    ```

2.  **Create a virtual environment** (recommended):
    ```bash
    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    # Mac/Linux
    source .venv/bin/activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

### Running Locally

1.  **Start the server**:
    ```bash
    python app.py
    # or
    gunicorn app:app
    ```

2.  **Access the bot**:
    Open your browser and navigate to `http://127.0.0.1:5000/`.


##  Usage

### Standard Flow
1.  Open the bot.
2.  Enter your name.
3.  Answer questions about loan amount and tenure.
4.  Provide mobile number for verification.
5.  Upload salary slip (if prompted).
6.  Download your sanction letter if approved.

