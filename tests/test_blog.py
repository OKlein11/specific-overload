import pytest
from overload.db import get_db

def test_index(client,auth):
    response = client.get("/")
    assert b"Log In" in response.data #test log in button appears
    assert b"Register" in response.data # test register button appears

    auth.login() # log in to auth1 user
    response = client.get("/")
    assert b"Log Out" in response.data # assert logout button appears
    assert b"test 1" in response.data # assert post appears
    assert b"by auth5 on 2018-01-01" in response.data #assert byline appears
    assert b"test\nbody" in response.data # assert body appears
    assert b'href="/1/update"' not in response.data #assert update button doesn't appear

    auth.login(username="auth5",password="auth5") #login as auth5
    response = client.get("/")
    assert b'href="/1/update"' in response.data # assert edit button appears for own post
    assert b'href="/2/update"' not in response.data # assert edit button does not appear for other's posts

    auth.login(username="auth10",password="auth10")
    response = client.get("/")
    assert b'href="/1/update"' in response.data # assert edit button appears for all posts
    assert b'href="/2/update"' in response.data

@pytest.mark.parametrize("path",(
    "/create",
    "/1/update",
    "/1/delete",
    ))
def test_login_required(client, path): #Checks the incoming post requests and mkaes sure that user is redirected to login page if not logged in
    response = client.post(path)
    assert response.headers["Location"] == "/auth/login"

@pytest.mark.parametrize(("path", "authority"),(
    ("/create",5),
    ("/1/update",5),
    ("/1/delete",5),
    ))
def test_not_enough_authority(client, auth,path,authority): # checks incoming post requests to make sure users have enough authority
    users = [("auth1",1),("auth5",5),("auth10",10)]
    for user in users:
        auth.login(username=user[0],password=user[0])
        if user[1] < authority:
            response = client.post(path)
            assert response.status_code == 403
    

def test_author_required(client,auth): # Tests to make sure you musts be the author of the post to update and delete it

    auth.login(username="auth5", password="auth5")

    assert client.post("/2/update").status_code == 403
    assert client.post("/2/delete").status_code == 403



@pytest.mark.parametrize("path", (
    "/3/update",
    "/3/delete"
))
def test_exists_required(client,auth,path): # Tests to make sure requests for posts that do not exist return 404s
    auth.login(username="auth5",password="auth5")
    assert client.post(path).status_code == 404


def test_create(client, auth, app): # Tests whether the /create page works
    auth.login(username="auth5",password="auth5")
    assert client.get("/create").status_code == 200
    client.post("/create", data={"title": "created", "body":""})
    with app.app_context():
        db = get_db()
        count = db.execute("SELECT COUNT(id) FROM post").fetchone()[0]
        assert count == 3

@pytest.mark.parametrize(("username","password"),(
    ("auth5","auth5"),
    ("auth10","auth10")))
def test_update(client, auth, app,username,password): # Tests whether the update page works for both the owner and an auth10
    auth.login(username=username,password=password)
    assert client.get("/1/update").status_code == 200
    client.post("/1/update", data={"title":"updated","body":""})

    with app.app_context():
        db=get_db()
        post = db.execute("SELECT * FROM post WHERE id = 1").fetchone()
        assert post["title"] == "updated"
    
@pytest.mark.parametrize("path", (
    "/create",
    "/1/update",
))
def test_create_update_validate(client, auth, path): # Tests to make sure not having a title throws the correct error
    auth.login(username="auth5",password="auth5")
    response = client.post(path, data={"title":"","body":""})
    assert b"Title is required." in response.data

@pytest.mark.parametrize(("username","password"),(
    ("auth5","auth5"),
    ("auth10","auth10")))
def test_delete(client,auth,app,username,password): # Tests to make sure the delete page works for the author and an auth10
    auth.login(username=username,password=password)
    response = client.post("/1/delete")
    assert response.headers["Location"] == "/"

    with app.app_context():
        db = get_db()
        post = db.execute("SELECT * FROM post WHERE id = 1").fetchone()
        assert post is None