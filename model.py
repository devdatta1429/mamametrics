from flask import Flask, render_template, request, redirect, session
from db import get_connection
import joblib

app = Flask(__name__)
app.secret_key = "secret123"

# LOAD MODEL
model = joblib.load('models/model.pkl')

# ================= LOGIN =================
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (email, password)
        )
        user = cursor.fetchone()

        if user:
            session['user_id'] = user['id']
            return redirect('/form')
        else:
            return "Invalid Login ❌"

    return render_template('login.html')


# ================= FORM =================
@app.route('/form', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':

        # GET VALUES
        data = [
            int(request.form['age_mother']),
            float(request.form['weight_before_preg']),
            float(request.form['weight_during_preg']),
            int(request.form['height_cm']),
            float(request.form['bmi']),
            float(request.form['hemoglobin']),
            int(request.form['pcos_status']),
            int(request.form['age_father']),
            int(request.form['yrs_of_mrg']),
            int(request.form['no_of_misscarg']),

            int(request.form['exercise_t']),
            int(request.form['exercise_b']),
            int(request.form['exercise_p']),

            int(request.form['screen_t']),
            int(request.form['screen_b']),
            int(request.form['screen_p']),

            int(request.form['sleep_t']),
            int(request.form['sleep_b']),
            int(request.form['sleep_p']),

            int(request.form['outside_food_t']),
            int(request.form['outside_food_b']),
            int(request.form['outside_food_p']),

            int(request.form['tea_coffee_t']),
            int(request.form['tea_coffee_b']),
            int(request.form['tea_coffee_p']),

            int(request.form['smoking_t']),
            int(request.form['smoking_b']),
            int(request.form['smoking_p']),

            int(request.form['alcohol_t']),
            int(request.form['alcohol_b']),
            int(request.form['alcohol_p']),

            int(request.form['happiness_status']),
            int(request.form['intercourse_freq'])
        ]

        # PREDICT
        prediction = model.predict([data])[0]

        # CONVERT BACK TO TEXT
        result_map = {0: 'Low', 1: 'Medium', 2: 'High'}
        result = result_map[prediction]

        # SAVE TO DB
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO predictions (risk_result)
        VALUES (%s)
        """, (result,))

        conn.commit()

        return redirect('/dashboard')

    return render_template('form.html')


# ================= DASHBOARD =================
@app.route('/dashboard')
def dashboard():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) as total FROM users")
    total_users = cursor.fetchone()['total']

    cursor.execute("SELECT risk_result, COUNT(*) as count FROM predictions GROUP BY risk_result")
    risk_data = cursor.fetchall()

    return render_template('dashboard.html',
                           total_users=total_users,
                           risk_data=risk_data)


# ================= RUN =================
if __name__ == '__main__':
    app.run(debug=True)