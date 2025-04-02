from flask import Flask, render_template, request, redirect, url_for, flash, session, abort, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hr.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# -------------------------------
# Models
# -------------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_manager = db.Column(db.Boolean, default=False)
    leave_balance = db.Column(db.Integer, default=20)  # จำนวนวันลาเริ่มต้น

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class LeaveRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.String(255))
    status = db.Column(db.String(20), default='Pending')  # Pending, Approved, Rejected
    applied_on = db.Column(db.DateTime, default=datetime.utcnow)
    approved_on = db.Column(db.DateTime, nullable=True)

    employee = db.relationship('User', backref=db.backref('leave_requests', lazy=True))

# -------------------------------
# Decorators
# -------------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('กรุณาเข้าสู่ระบบ', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def manager_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = User.query.get(session.get('user_id'))
        if not user or not user.is_manager:
            flash('เฉพาะผู้จัดการเท่านั้น', 'warning')
            return redirect(url_for('hr_dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# -------------------------------
# Public Website Routes (สำหรับสาธารณะ)
# -------------------------------
@app.route('/')
def public_index():
    return render_template('public/index.html')

@app.route('/about')
def public_about():
    return render_template('public/about.html')

@app.route('/contact')
def public_contact():
    return render_template('public/contact.html')

# -------------------------------
# Static Files (สำหรับรูปภาพและโลโก้)
# -------------------------------
@app.route('/images/<path:filename>')
def serve_images(filename):
    return send_from_directory('static/images', filename)

@app.route('/logo/<path:filename>')
def serve_logo(filename):
    return send_from_directory('static/logo', filename)

# -------------------------------
# HR System - Authentication and Dashboard
# -------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            flash('เข้าสู่ระบบสำเร็จ', 'success')
            return redirect(url_for('hr_dashboard'))
        else:
            flash('ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง', 'danger')
    return render_template('hr/login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('ออกจากระบบแล้ว', 'info')
    return redirect(url_for('login'))

@app.route('/hr')
@login_required
def hr_dashboard():
    user = User.query.get(session['user_id'])
    leave_requests = LeaveRequest.query.filter_by(employee_id=user.id).order_by(LeaveRequest.applied_on.desc()).all()
    return render_template('hr/dashboard.html', user=user, leave_requests=leave_requests)

# -------------------------------
# HR System - Leave Application
# -------------------------------
@app.route('/hr/apply_leave', methods=['GET', 'POST'])
@login_required
def apply_leave():
    if request.method == 'POST':
        start_date_str = request.form['start_date']
        end_date_str = request.form['end_date']
        reason = request.form['reason']
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            if start_date > end_date:
                flash('วันที่เริ่มต้องน้อยกว่าวันที่สิ้นสุด', 'danger')
                return redirect(url_for('apply_leave'))
            user = User.query.get(session['user_id'])
            delta = (end_date - start_date).days + 1
            if delta > user.leave_balance:
                flash('จำนวนวันลาที่ขอเกินจากจำนวนวันลาคงเหลือ', 'danger')
                return redirect(url_for('apply_leave'))
            leave_request = LeaveRequest(employee_id=user.id, start_date=start_date, end_date=end_date, reason=reason)
            db.session.add(leave_request)
            db.session.commit()
            flash('ส่งคำร้องลาเรียบร้อย', 'success')
            return redirect(url_for('hr_dashboard'))
        except ValueError:
            flash('รูปแบบวันที่ไม่ถูกต้อง', 'danger')
    return render_template('hr/apply_leave.html')

@app.route('/hr/leave_details/<int:leave_id>')
@login_required
def leave_details(leave_id):
    leave = LeaveRequest.query.get_or_404(leave_id)
    # เฉพาะเจ้าของคำร้องเท่านั้นที่สามารถดูรายละเอียดได้
    if leave.employee_id != session.get('user_id'):
        abort(403)
    return render_template('hr/leave_details.html', leave=leave)

# -------------------------------
# HR System - Manager (Approval)
# -------------------------------
@app.route('/hr/manager')
@login_required
@manager_required
def manager_dashboard():
    pending_leaves = LeaveRequest.query.filter_by(status='Pending').order_by(LeaveRequest.applied_on.desc()).all()
    return render_template('hr/manager_dashboard.html', pending_leaves=pending_leaves)

@app.route('/hr/manager/approve/<int:leave_id>', methods=['POST'])
@login_required
@manager_required
def approve_leave(leave_id):
    leave = LeaveRequest.query.get_or_404(leave_id)
    action = request.form.get('action')
    if action == 'approve':
        leave.status = 'Approved'
        leave.approved_on = datetime.utcnow()
        delta = (leave.end_date - leave.start_date).days + 1
        employee = User.query.get(leave.employee_id)
        employee.leave_balance -= delta
    elif action == 'reject':
        leave.status = 'Rejected'
    else:
        flash('การกระทำไม่ถูกต้อง', 'danger')
        return redirect(url_for('manager_dashboard'))
    db.session.commit()
    flash('ปรับปรุงสถานะคำร้องลาแล้ว', 'success')
    return redirect(url_for('manager_dashboard'))

# -------------------------------
# HR System - Leave Balance Overview
# -------------------------------
@app.route('/hr/leave_balance')
@login_required
def leave_balance():
    user = User.query.get(session['user_id'])
    return render_template('hr/leave_balance.html', user=user)

# -------------------------------
# Command สำหรับสร้างฐานข้อมูลและข้อมูลตัวอย่าง
# -------------------------------
@app.cli.command('initdb')
def initdb():
    db.create_all()
    # สร้างผู้จัดการและพนักงานตัวอย่าง
    if not User.query.filter_by(username='manager').first():
        manager = User(username='manager', is_manager=True, leave_balance=30)
        manager.set_password('manager123')
        db.session.add(manager)
    if not User.query.filter_by(username='employee').first():
        employee = User(username='employee', is_manager=False, leave_balance=20)
        employee.set_password('employee123')
        db.session.add(employee)
    db.session.commit()
    print('Initialized the database.')

if __name__ == '__main__':
    app.run(debug=True)
