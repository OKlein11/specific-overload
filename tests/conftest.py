import os
import tempfile

import pytest
from overload import create_app
from overload.db import get_db, init_db

with open(os.path.join(os.path.dirname(__file__), "data.sql"), "rb") as f:
    _data_sql = f.read().decode("utf8")

@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({
        "TESTING": True,
        "DATABASE": db_path
    })

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)
    
    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

class AuthActions(object):
    def __init__(self, client):
        self.client = client
    
    def login(self, username="auth1", password="auth1"):
        return self.client.post(
            "/auth/login",
            data={"username":username, "password": password}
        )
    
    def logout(self):
        return self.client.get("/auth/logout")

@pytest.fixture
def auth(client):
    return AuthActions(client)