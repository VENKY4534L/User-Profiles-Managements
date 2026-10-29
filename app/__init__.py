from pathlib import Path
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(test_config=None):
    load_dotenv()
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object("config.Config")
    if test_config:
        app.config.update(test_config)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    db.init_app(app)
    from app.routes import bp
    app.register_blueprint(bp)
    with app.app_context():
        from app import models  # noqa: F401
        db.create_all()
    return app
