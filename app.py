from flask import Flask, render_template, request, redirect
import mysql.connector
from datetime import datetime

app = Flask(__name__)

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Vishal@2004",
    database="parking_db"
)
cursor = db.cursor()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/entry', methods=['GET', 'POST'])
def entry():
    if request.method == 'POST':
        vehicle_number = request.form['vehicle_number']
        vehicle_type = request.form['vehicle_type']
        entry_time = datetime.now()
        cursor.execute("INSERT INTO parking (vehicle_number, vehicle_type, entry_time) VALUES (%s, %s, %s)",
                       (vehicle_number, vehicle_type, entry_time))
        db.commit()
        return redirect('/')
    return render_template('entry.html')

@app.route('/exit', methods=['GET', 'POST'])
def exit():
    if request.method == 'POST':
        vehicle_number = request.form['vehicle_number']
        exit_time = datetime.now()
        cursor.execute("SELECT id, entry_time FROM parking WHERE vehicle_number=%s AND exit_time IS NULL",
                       (vehicle_number,))
        result = cursor.fetchone()
        if result:
            id, entry_time = result
            duration = (exit_time - entry_time).seconds / 3600
            fee = round(duration * 20, 2)
            cursor.execute("UPDATE parking SET exit_time=%s, fee=%s WHERE id=%s",
                           (exit_time, fee, id))
            db.commit()
        return redirect('/')
    return render_template('exit.html')

@app.route('/view')
def view():
    cursor.execute("SELECT * FROM parking")
    data = cursor.fetchall()
    return render_template('view.html', vehicles=data)

@app.route('/search', methods=['GET', 'POST'])
def search():
    vehicles = []
    if request.method == 'POST':
        vehicle_number = request.form['vehicle_number']
        cursor.execute("SELECT * FROM parking WHERE vehicle_number=%s", (vehicle_number,))
        vehicles = cursor.fetchall()
    return render_template('search.html', vehicles=vehicles)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin123':
            return redirect('/admin/dashboard')
        else:
            return "Invalid credentials", 401
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    cursor.execute("SELECT COUNT(*) FROM parking")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM parking WHERE exit_time IS NULL")
    current = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(fee) FROM parking WHERE fee IS NOT NULL")
    revenue = cursor.fetchone()[0] or 0

    return render_template('dashboard.html', total=total, current=current, revenue=revenue)

if __name__ == '__main__':
    app.run(debug=True)