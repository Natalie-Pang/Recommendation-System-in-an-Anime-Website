import pytest
from flask import url_for
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
from website import create_app
from website.models import db, User

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    with app.app_context():
        yield app

@pytest.fixture
def client(app):
    return app.test_client()

