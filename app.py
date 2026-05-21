from flask import Flask, render_template, request, redirect, session
from db import get_connection
from flask_cors import CORS
from dotenv import load_dotenv
import os
import mysql.connector
import os
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)
CORS(app)

load_dotenv()

def get_connection():

    return mysql.connector.connect(
        host=os.getenv("MYSQLHOST"),
        user=os.getenv("MYSQLUSER"),
        password=os.getenv("MYSQLPASSWORD"),
        database=os.getenv("MYSQLDATABASE"),
        port=int(os.getenv("MYSQLPORT"))
    )

app.secret_key = os.getenv("SECRET_KEY")


@app.route("/")
def home():
    return "MamaMetrics Backend Running"


# ================= LOGIN =================
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s",
                       (email, password))
        user = cursor.fetchone()

        if user:
            session['user_id'] = user['id']
            return redirect('/dashboard')
        else:
            return "Invalid login"

    return render_template('login.html')


# ================= REGISTER =================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("INSERT INTO users(name,email,password) VALUES(%s,%s,%s)",
                       (name, email, password))
        conn.commit()

        return redirect('/')

    return render_template('register.html')


# ================= FORM =================
@app.route('/form', methods=['GET', 'POST'])
def form():

    # Check login
    if 'user_id' not in session:
        return redirect('/')

    if request.method == 'POST':
        patient_name = request.form['patient_name']
        age_mother = int(request.form['age_mother'])
        bmi = float(request.form['bmi'])
        hemoglobin = float(request.form['hemoglobin'])
        stress_level = int(request.form['stress_level'])
        work_hours = int(request.form['work_hours'])
        smoking_p = int(request.form['smoking_p'])
        alcohol_p = int(request.form['alcohol_p'])

        # ========= RULE-BASED LOGIC =========

        # Risk
        if stress_level > 7 or smoking_p == 1 or alcohol_p == 1:
            risk = "High"
        elif stress_level > 4:
            risk = "Medium"
        else:
            risk = "Low"

        # Delivery
        if age_mother > 35 or bmi > 30:
            c_section = 1
            vaginal = 0
        else:
            c_section = 0
            vaginal = 1

        # NICU
        if hemoglobin < 10 or stress_level > 8:
            nicu = "Yes"
        else:
            nicu = "No"

        # Preterm
        if stress_level > 8 or work_hours > 10:
            preterm = 1
            fullterm = 0
        else:
            preterm = 0
            fullterm = 1

        # Jaundice
        if hemoglobin < 9:
            jaundice = 1
        else:
            jaundice = 0

        predicted_weight = 2.5 + (hemoglobin * 0.1)

        # ========= SAVE =========
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
INSERT INTO predictions
    (
    user_id,
    patient_name,
    C_section,
    Vaginal_delievery,
    risk_result,
    predicted_weight,
    nicu_risk,
    preterm,
    fullterm,
    jaundice
    )

    VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """,
    (
    session['user_id'],
    patient_name,
    c_section,
    vaginal,
    risk,
    predicted_weight,
    nicu,
    preterm,
    fullterm,
    jaundice

    ))

        conn.commit()

        return redirect('/dashboard')

    return render_template('form.html')


# ================= DASHBOARD =================

@app.route('/dashboard')
def dashboard():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
    "SELECT * FROM predictions WHERE user_id=%s",
    (session['user_id'],))
    data = cursor.fetchall()

    return render_template('dashboard.html', data=data)

# ================= LOGOUT =================
@app.route('/logout')
def logout():

    session.clear()

    return redirect('/')


# ================= DELETE =================

@app.route('/delete/<int:id>')
def delete_prediction(id):

    # Check login
    if 'user_id' not in session:
        return redirect('/')

    conn = get_connection()
    cursor = conn.cursor()

    # Delete only logged-in user's prediction
    cursor.execute(
        "DELETE FROM predictions WHERE id=%s AND user_id=%s",
        (id, session['user_id'])
    )

    conn.commit()

    return redirect('/dashboard')
# ================= RUN =================
if __name__ == '__main__':
    app.run(debug=True)
    