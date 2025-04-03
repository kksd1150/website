import click
from extensions import db
from models import User
from flask import current_app

@click.command('initdb')
def init_db_command():
    db.drop_all()
    db.create_all()
    # สร้างผู้ใช้งานตัวอย่าง
    if not User.query.filter_by(username='manager').first():
        manager = User(username='manager', employee_code='M001', is_manager=True, leave_balance=30, job_title='Manager', section='HR', supervisor='')
        manager.set_password('manager123')
        db.session.add(manager)
    if not User.query.filter_by(username='employee').first():
        employee = User(username='employee', employee_code='E001', is_manager=False, leave_balance=20, job_title='Staff', section='HR', supervisor='manager')
        employee.set_password('employee123')
        db.session.add(employee)
    db.session.commit()
    click.echo('Initialized the database.')

def register_commands(app):
    app.cli.add_command(init_db_command)
import click
from extensions import db
from models import User
from flask import current_app

@click.command('initdb')
def init_db_command():
    db.drop_all()
    db.create_all()
    # สร้างผู้ใช้งานตัวอย่าง
    if not User.query.filter_by(username='manager').first():
        manager = User(username='manager', employee_code='M001', is_manager=True, leave_balance=30, job_title='Manager', section='HR', supervisor='')
        manager.set_password('manager123')
        db.session.add(manager)
    if not User.query.filter_by(username='employee').first():
        employee = User(username='employee', employee_code='E001', is_manager=False, leave_balance=20, job_title='Staff', section='HR', supervisor='manager')
        employee.set_password('employee123')
        db.session.add(employee)
    db.session.commit()
    click.echo('Initialized the database.')

def register_commands(app):
    app.cli.add_command(init_db_command)
