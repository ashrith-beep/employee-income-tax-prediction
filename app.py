# app.py
# Main Flask file for Employee Tax Prediction project
# Semester 6 - Full Stack Development Project

import os
import re
import json
import joblib
import sqlite3
from datetime import datetime
from functools import wraps

from flask import (Flask, render_template, request, redirect,
                   url_for, session, flash, jsonify)
from werkzeug.security import generate_password_hash, check_password_hash

from database import init_db, get_db

# create flask app
app = Flask(__name__)
app.secret_key = 'tax_predict_secret_key'
BASE_DIR = os.path.dirname(__file__)

# load the ML model we trained in model.py
MODEL_PATH = os.path.join(BASE_DIR, 'tax_model.pkl')
model = None

def load_model():
    global model
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        print("Model loaded successfully")
    else:
        print("Warning: tax_model.pkl not found. Run model.py first.")


# decorator to check if user is logged in
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


# decorator to check if user is admin
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('is_admin'):
            flash('Access denied. Admins only.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated


# simple email format check using regex
def is_valid_email(email):
    return re.match(r'^[\w\.\+\-]+@[\w\-]+\.[a-zA-Z]{2,}$', email) is not None


# generate tax saving tips based on user inputs
def tax_saving_suggestions(salary, investments, deductions, other_income):
    suggestions = []

    # check how much 80C limit is remaining
    max_80c = 150000
    remaining_80c = max_80c - int(investments)
    if remaining_80c > 0:
        suggestions.append({
            'icon': '📈',
            'title': 'Maximize Section 80C Investments',
            'detail': (
                f"You can still invest ₹{remaining_80c:,} more under Section 80C "
                f"(e.g., ELSS, PPF, LIC, NSC) to reduce your taxable income further."
            )
        })
    else:
        suggestions.append({
            'icon': '✅',
            'title': 'Section 80C Fully Utilized',
            'detail': (
                "Great! You have maximized your ₹1,50,000 limit under Section 80C. "
                "Consider NPS (Section 80CCD) for an additional ₹50,000 deduction."
            )
        })

    # suggest health insurance deduction
    if int(salary) > 500000 and int(deductions) < 25000:
        suggestions.append({
            'icon': '🏥',
            'title': 'Claim Health Insurance Premium (Section 80D)',
            'detail': (
                "You can claim up to ₹25,000 per year for health insurance premium "
                "for self & family under Section 80D. If parents are senior citizens, "
                "the limit extends to ₹50,000."
            )
        })
    else:
        suggestions.append({
            'icon': '🏠',
            'title': 'Consider a Home Loan for HRA Benefit',
            'detail': (
                "If you pay rent, claim House Rent Allowance (HRA) exemption. "
                "If you have a home loan, interest up to ₹2,00,000 is deductible "
                "under Section 24(b), reducing your taxable income significantly."
            )
        })

    return suggestions


# tax slab calculation as per Indian income tax rules
def compute_tax_by_slabs(taxable_income):
    # Indian income tax slabs (old regime):
    # upto 2.5 lakh = 0%
    # 2.5 to 5 lakh = 5%
    # 5 to 10 lakh  = 20%
    # above 10 lakh = 30%
    taxable = max(0.0, float(taxable_income))
    if taxable <= 250000:
        return 0.0
    elif taxable <= 500000:
        return (taxable - 250000) * 0.05
    elif taxable <= 1000000:
        return 12500 + (taxable - 500000) * 0.20
    else:
        return 112500 + (taxable - 1000000) * 0.30


# predict tax using ML model or fallback to slab formula
def predict_tax_from_inputs(salary, other_income, investments, deductions, age):
    if model is None:
        # if model not loaded, use formula based calculation
        gross = float(salary) + float(other_income)
        taxable = max(0.0, gross - float(investments) - float(deductions) - 50000)
        return round(compute_tax_by_slabs(taxable), 2)
    else:
        import numpy as np
        features = [[float(salary), float(other_income),
                     float(investments), float(deductions), int(age)]]
        return round(float(model.predict(features)[0]), 2)


# ---- Routes ----

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('predict'))
    return redirect(url_for('login'))


# login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('predict'))

    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()

        if not email or not password:
            flash('Please fill in all fields.', 'danger')
            return render_template('login.html', email=email)

        if not is_valid_email(email):
            flash('Invalid email format.', 'danger')
            return render_template('login.html', email=email)

        db   = get_db()
        user = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        db.close()

        if user is None or not check_password_hash(user['password'], password):
            flash('Invalid credentials. Please check your email and password.', 'danger')
            return render_template('login.html', email=email)

        session['user_id']  = user['id']
        session['email']    = user['email']
        session['is_admin'] = bool(user['is_admin'])
        session.pop('skip_mode', None)
        session.pop('skip_count', None)
        flash(f'Welcome back, {user["email"]}!', 'success')
        return redirect(url_for('predict'))

    return render_template('login.html')


# register page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('predict'))

    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        confirm  = request.form.get('confirm_password', '').strip()

        errors = []
        if not email or not password or not confirm:
            errors.append('All fields are required.')
        if email and not is_valid_email(email):
            errors.append('Please enter a valid email address.')
        if password and len(password) < 6:
            errors.append('Password must be at least 6 characters.')
        if password and confirm and password != confirm:
            errors.append('Passwords do not match.')

        if errors:
            for e in errors:
                flash(e, 'danger')
            return render_template('register.html', email=email)

        db = get_db()
        existing = db.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone()
        if existing:
            flash('An account with this email already exists. Please login.', 'warning')
            db.close()
            return render_template('register.html', email=email)

        db.execute(
            'INSERT INTO users (email, password) VALUES (?, ?)',
            (email, generate_password_hash(password))
        )
        db.commit()
        db.close()

        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


# guest mode - allows 3 predictions without login
@app.route('/skip')
def skip():
    session['skip_mode']  = True
    session['skip_count'] = 0
    return redirect(url_for('predict'))


# main prediction page
@app.route('/predict', methods=['GET', 'POST'])
def predict():
    is_logged_in = 'user_id' in session
    is_skip      = session.get('skip_mode', False)

    if not is_logged_in and not is_skip:
        return redirect(url_for('login'))

    # limit guest users to 3 predictions only
    if is_skip and not is_logged_in:
        count = session.get('skip_count', 0)
        if request.method == 'POST' and count >= 3:
            flash('You have used all 3 free predictions. Please register to continue.', 'warning')
            return render_template('predict.html',
                                   is_skip=True,
                                   skip_count=count,
                                   skip_remaining=0,
                                   limit_reached=True)

    if request.method == 'POST':
        try:
            salary      = float(request.form['annual_salary'])
            other_inc   = float(request.form.get('other_income', 0) or 0)
            investments = float(request.form.get('investments', 0)  or 0)
            deductions  = float(request.form.get('deductions', 0)   or 0)
            age         = int(request.form.get('age', 30)           or 30)
        except (ValueError, KeyError):
            flash('Please enter valid numeric values.', 'danger')
            return render_template('predict.html',
                                   is_skip=is_skip,
                                   skip_count=session.get('skip_count', 0),
                                   skip_remaining=max(0, 3 - session.get('skip_count', 0)))

        # call prediction function
        predicted_tax = predict_tax_from_inputs(salary, other_inc, investments, deductions, age)

        # save prediction to database for logged in users
        if is_logged_in:
            db = get_db()
            db.execute('''
                INSERT INTO predictions
                (user_id, annual_salary, other_income, investments, deductions, age, predicted_tax)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (session['user_id'], salary, other_inc, investments, deductions, age, predicted_tax))
            db.commit()
            db.close()

        # update skip count for guest users
        if is_skip and not is_logged_in:
            session['skip_count'] = session.get('skip_count', 0) + 1

        gross_income   = salary + other_inc
        total_deduct   = investments + deductions + 50000
        taxable_income = max(0, gross_income - total_deduct)

        # data for chart
        chart_data = {
            'labels': ['Gross Income', 'Total Deductions', 'Taxable Income', 'Predicted Tax'],
            'values': [gross_income, total_deduct, taxable_income, predicted_tax],
        }

        suggestions = tax_saving_suggestions(salary, investments, deductions, other_inc)

        # store result in session to show on result page
        session['last_result'] = {
            'salary':         salary,
            'other_income':   other_inc,
            'investments':    investments,
            'deductions':     deductions,
            'age':            age,
            'predicted_tax':  predicted_tax,
            'gross_income':   gross_income,
            'taxable_income': taxable_income,
            'chart_data':     chart_data,
            'suggestions':    suggestions,
        }

        return redirect(url_for('result'))

    skip_count     = session.get('skip_count', 0)
    skip_remaining = max(0, 3 - skip_count)
    return render_template('predict.html',
                           is_skip=is_skip,
                           skip_count=skip_count,
                           skip_remaining=skip_remaining,
                           limit_reached=False)


# result page - shows prediction output
@app.route('/result')
def result():
    is_logged_in = 'user_id' in session
    is_skip      = session.get('skip_mode', False)

    if not is_logged_in and not is_skip:
        return redirect(url_for('login'))

    data = session.get('last_result')
    if not data:
        return redirect(url_for('predict'))

    return render_template('result.html',
                           data=data,
                           is_logged_in=is_logged_in,
                           chart_data_json=json.dumps(data['chart_data']))


# prediction history for logged in users
@app.route('/history')
@login_required
def history():
    db = get_db()
    records = db.execute('''
        SELECT * FROM predictions
        WHERE user_id = ?
        ORDER BY created_at DESC
    ''', (session['user_id'],)).fetchall()
    db.close()
    return render_template('history.html', records=records)


# admin panel - only for admin users
@app.route('/admin')
@login_required
@admin_required
def admin():
    db = get_db()
    users = db.execute('SELECT * FROM users ORDER BY created_at DESC').fetchall()
    predictions = db.execute('''
        SELECT p.*, u.email
        FROM predictions p
        JOIN users u ON p.user_id = u.id
        ORDER BY p.created_at DESC
    ''').fetchall()
    db.close()
    return render_template('admin.html', users=users, predictions=predictions)


# Initialize database and load the ML model so they are ready for WSGI servers (like Gunicorn/Waitress)
init_db()
load_model()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
