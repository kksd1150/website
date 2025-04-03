from flask import render_template, request, redirect, url_for, flash, Blueprint
from models import User, LeaveRequest
from extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash

admin_bp = Blueprint('admin', __name__, template_folder='templates/admin')

@admin_bp.route('/data_entry', methods=['GET', 'POST'])
def data_entry():
    # หน้าเว็บสำหรับ admin คีย์ข้อมูลพนักงานและการลา
    if request.method == 'POST':
        if 'employee_submit' in request.form:
            username = request.form['username'].strip()
            password = request.form['password'].strip()
            employee_code = request.form['employee_code'].strip()
            job_title = request.form['job_title'].strip()
            section = request.form['section'].strip()
            supervisor = request.form['supervisor'].strip()
            if not (username and password and employee_code):
                flash('Username, Password, and Employee Code are required.', 'danger')
            else:
                if User.query.filter_by(username=username).first():
                    flash('Username already exists.', 'danger')
                else:
                    new_user = User(username=username, employee_code=employee_code, job_title=job_title, section=section, supervisor=supervisor)
                    new_user.set_password(password)
                    db.session.add(new_user)
                    db.session.commit()
                    flash('Employee added successfully.', 'success')
        elif 'leave_submit' in request.form:
            employee_id = request.form['employee_id'].strip()
            leave_type = request.form['leave_type'].strip()
            start_date_str = request.form['start_date'].strip()
            end_date_str = request.form['end_date'].strip()
            reason = request.form['reason'].strip()
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                new_leave = LeaveRequest(employee_id=employee_id, leave_type=leave_type, start_date=start_date, end_date=end_date, reason=reason)
                db.session.add(new_leave)
                db.session.commit()
                flash('Leave request added successfully.', 'success')
            except ValueError:
                flash('Invalid date format. Use YYYY-MM-DD.', 'danger')
    return render_template('data_entry.html')
