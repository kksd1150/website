from flask import render_template, redirect, url_for, flash, request, session, abort
from models import User, LeaveRequest
from extensions import db
from functools import wraps
from datetime import datetime
from . import hr_bp  # ใช้ hr_bp จาก __init__.py

@hr_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            flash('Logged in successfully.', 'success')
            return redirect(url_for('hr.dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html')

@hr_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out.', 'info')
    return redirect(url_for('hr.login'))

@hr_bp.route('/dashboard')
def dashboard():
    user = User.query.get(session['user_id'])
    leave_requests = LeaveRequest.query.filter_by(employee_id=user.id).order_by(LeaveRequest.applied_on.desc()).all()
    return render_template('dashboard.html', user=user, leave_requests=leave_requests)

@hr_bp.route('/apply_leave', methods=['GET', 'POST'])
def apply_leave():
    if request.method == 'POST':
        start_date_str = request.form['start_date']
        end_date_str = request.form['end_date']
        leave_type = request.form['leave_type']
        reason = request.form['reason']
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            if start_date > end_date:
                flash('Start date must be before end date.', 'danger')
                return redirect(url_for('hr.apply_leave'))
            user = User.query.get(session['user_id'])
            delta = (end_date - start_date).days + 1
            if delta > user.leave_balance:
                flash('Requested leave days exceed available leave balance.', 'danger')
                return redirect(url_for('hr.apply_leave'))
            new_leave = LeaveRequest(
                employee_id=user.id,
                leave_type=leave_type,
                start_date=start_date,
                end_date=end_date,
                reason=reason
            )
            db.session.add(new_leave)
            db.session.commit()
            flash('Leave request submitted.', 'success')
            return redirect(url_for('hr.dashboard'))
        except ValueError:
            flash('Invalid date format. Use YYYY-MM-DD.', 'danger')
    return render_template('apply_leave.html')

@hr_bp.route('/leave_details/<int:leave_id>')
def leave_details(leave_id):
    leave = LeaveRequest.query.get_or_404(leave_id)
    if leave.employee_id != session.get('user_id'):
        abort(403)
    return render_template('leave_details.html', leave=leave)

@hr_bp.route('/leave_balance')
def leave_balance():
    user = User.query.get(session['user_id'])
    return render_template('leave_balance.html', user=user)

@hr_bp.route('/manager_dashboard')
def manager_dashboard():
    pending_leaves = LeaveRequest.query.filter_by(status='Pending').order_by(LeaveRequest.applied_on.desc()).all()
    return render_template('manager_dashboard.html', pending_leaves=pending_leaves)

@hr_bp.route('/manager/approve/<int:leave_id>', methods=['POST'])
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
        flash('Invalid action.', 'danger')
        return redirect(url_for('hr.manager_dashboard'))
    db.session.commit()
    flash('Leave status updated.', 'success')
    return redirect(url_for('hr.manager_dashboard'))
