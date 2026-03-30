Employee Tax Prediction
=======================
Semester 6 - Full Stack Development (FSD) Project
Academic Year: 2025-26

---

Project Description:
--------------------
This is a web application that predicts income tax for employees
based on their annual salary, investments, and deductions.
We used Flask for the backend, SQLite for the database, and
scikit-learn (Random Forest) for the ML model.

Tax slabs used (Indian Old Regime):
  - Up to Rs. 2,50,000        : 0%
  - Rs. 2,50,001 - 5,00,000  : 5%
  - Rs. 5,00,001 - 10,00,000 : 20%
  - Above Rs. 10,00,000      : 30%

Features:
---------
  - User login and registration
  - Guest mode (3 free predictions without login)
  - Tax prediction using ML model
  - Tax saving suggestions
  - Prediction history for registered users
  - Admin panel to manage users and predictions

---

How to Run:
-----------
1. Install dependencies:
      pip install -r requirements.txt

2. Train the model (only once):
      python model.py

3. Start the app:
      python app.py

4. Open browser and go to:
      http://localhost:5000

Admin Login:
   Email   : admin@tax.com
   Password: admin123

---

Technologies Used:
------------------
  - Python 3.x
  - Flask (web framework)
  - SQLite (database)
  - scikit-learn (machine learning)
  - HTML, CSS, JavaScript (frontend)
  - Chart.js (graphs)

---

Note: This project is made for educational purposes only.
https://employee-income-tax-prediction.onrender.com/login

