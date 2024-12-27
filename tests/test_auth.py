import pytest
from flask import g, session
from overload.db import get_db

def test_register(client,app,auth):
    assert client.get("/auth/register").status_code == 200 #check page works
    response = client.post(
        "/auth/register", data={"username": "a", "password": "a"}
    ) 
    assert response.headers["Location"] == "/auth/login" #assert after registering you are redirected to login page

    with app.app_context():
        assert get_db().execute(
            "SELECT * FROM user WHERE username = 'a'",
        ).fetchone() is not None #assert the user is actually registered

    auth.login()
    response = client.get("/auth/register")
    assert response.headers["Location"] == "/" #assert that logged in users are redirected to the home apge

    auth.login(username="auth10",password="auth10")
    response = client.post(
        "/auth/register", data={"username": "b", "password": "b", "authority":5}
    )
    assert response.headers["Location"] == "/auth/login" #assert after registering you are redirected to login page
    with app.app_context():
        assert get_db().execute(
            "SELECT * FROM user WHERE username = 'b'",
        ).fetchone() is not None #assert the user is actually registered


    
@pytest.mark.parametrize(
    ("username","password","authority", "message"),
    (("","",None,b"Username is required."),
    ("a","",None,b"Password is required."),
    ("a","a",5,b"You do not have authority to create this user."),
    ("<script>","test",None,b"Username is not allowed. Please choose another."),
    ("auth1","auth1",None, b"already registered"),
))
def test_register_value_input(client,username,password,authority,message): # Tests whether bad entries throw correct errors
    if authority == None:
        data = {"username": username, "password":password}
    else:
        data = {"username": username, "password":password, "authority":authority}
    response = client.post(
        "/auth/register",
        data=data
    )
    assert message in response.data


def test_login(client, auth): # Tests whether login page works
    assert client.get("/auth/login").status_code == 200
    response = auth.login()
    assert response.headers["Location"] == "/"

    with client:
        client.get("/")
        assert session["user_id"] == 1
        assert g.user["username"] == "auth1"
    
@pytest.mark.parametrize(("username","password","message"),(
    ("a","test",b"Incorrect username."),
    ("auth1","a", b"Incorrect password."),
))
def test_login_validate_input(auth,username,password,message): # Tests that bad login entries throw correct errors
    response = auth.login(username,password)
    assert message in response.data

def test_logout(client,auth): # Tests the logout function
    auth.login()

    with client:
        auth.logout()
        assert "user_id" not in session