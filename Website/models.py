from extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    employee_code = db.Column(db.String(80), unique=True, nullable=False)
    is_manager = db.Column(db.Boolean, default=False)
    leave_balance = db.Column(db.Integer, default=20)
    job_title = db.Column(db.String(80), default='')
    section = db.Column(db.String(80), default='')
    supervisor = db.Column(db.String(80), default='')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class LeaveRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    leave_type = db.Column(db.String(80), nullable=False, default='')
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.String(255))
    status = db.Column(db.String(20), default='Pending')
    applied_on = db.Column(db.DateTime, default=datetime.utcnow)
    approved_on = db.Column(db.DateTime, nullable=True)

    employee = db.relationship('User', backref=db.backref('leave_requests', lazy=True))
