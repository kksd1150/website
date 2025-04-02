from flask import Flask, render_template, request, redirect, flash, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'
DATABASE = 'users.db'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                emp_id TEXT NOT NULL,
                fullname TEXT NOT NULL,
                jobtitle TEXT NOT NULL,
                section TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                ip_address TEXT NOT NULL,
                mac_address TEXT NOT NULL
            )
        ''')
        conn.commit()

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect(DATABASE) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.execute("SELECT * FROM users WHERE username=?", (username,))
            user = cur.fetchone()
        if user and check_password_hash(user['password'], password):
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('dashboard'))
        else:
            flash('ชื่อผู้ใช้งานหรือรหัสผ่านไม่ถูกต้อง')
    return render_template('logincsc.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

# ========== เพิ่ม route สำหรับหน้าอื่นๆ ตามที่ใช้ใน dashboard.html ==========
@app.route('/employee-directory')
def employee_directory():
    return render_template('employee-directory.html')

@app.route('/time-attendance')
def time_attendance():
    return render_template('time-attendance.html')

@app.route('/payroll')
def payroll():
    return render_template('payroll.html')

@app.route('/benefits')
def benefits():
    return render_template('benefits.html')

@app.route('/performance')
def performance():
    return render_template('performance.html')

@app.route('/recruitment')
def recruitment():
    return render_template('recruitment.html')

@app.route('/reports')
def reports():
    return render_template('reports.html')
# ===============================================================================

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        new_username = request.form['username']
        new_password = generate_password_hash(request.form['password'])
        new_emp_id = request.form['emp_id']
        new_fullname = request.form['fullname']
        new_jobtitle = request.form['jobtitle']
        new_section = request.form['section']
        new_role = request.form['role']
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ip_address = request.remote_addr or 'N/A'
        mac_address = "N/A"
        try:
            with sqlite3.connect(DATABASE) as conn:
                conn.execute("""INSERT INTO users 
                                (username, password, role, emp_id, fullname, jobtitle, section, timestamp, ip_address, mac_address)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                             (new_username, new_password, new_role, new_emp_id, new_fullname, new_jobtitle, new_section, current_time, ip_address, mac_address))
                conn.commit()
            flash('เพิ่มผู้ใช้งานใหม่สำเร็จ')
        except sqlite3.IntegrityError:
            flash('ชื่อผู้ใช้งานนี้มีอยู่แล้ว')
    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute("SELECT id, username, emp_id, fullname, role, jobtitle, section, timestamp, ip_address, mac_address FROM users")
        users = cur.fetchall()
    return render_template('admin.html', users=users)

@app.route('/admin/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    with sqlite3.connect(DATABASE) as conn:
        conn.execute("DELETE FROM users WHERE id=?", (user_id,))
        conn.commit()
    flash('ลบผู้ใช้งานเรียบร้อยแล้ว')
    return redirect(url_for('admin'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
