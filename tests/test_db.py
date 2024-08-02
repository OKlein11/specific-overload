import sqlite3

import pytest
from overload.db import get_db

def test_get_close(app):
    with app.app_context():
        db = get_db()
        assert db is get_db()

    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute("SELECT 1")
    
    assert "closed" in str(e.value)

def test_init_db_command(runner, monkeypatch):
    class Recorder(object):
        called = False
    
    def fake_init_db():
        Recorder.called = True
    
    monkeypatch.setattr("overload.db.init_db", fake_init_db)
    result = runner.invoke(args=["init-db"])
    assert "Initialized" in result.output
    assert Recorder.called

@pytest.mark.parametrize(("username","password","message"),
    (("test","test","created"),
    ("","","Username required."),
    ("test","","Password required."),
    ("auth1","auth1","already registered"))
)
def test_generate_superuser_command(app,runner,username,password,message):
    with app.app_context():
        result = runner.invoke(args=["generate-superuser",username,password])
    
    assert message in result.output

