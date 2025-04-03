#!/usr/bin/env python3
from flask import Flask
from config import Config
from extensions import db
from commands import register_commands
from blueprints.public import public_bp
from blueprints.hr import hr_bp
from blueprints.admin import admin_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    register_commands(app)
    app.register_blueprint(public_bp)
    app.register_blueprint(hr_bp, url_prefix='/hr')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
