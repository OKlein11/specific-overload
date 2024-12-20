import io
import pytest
import os
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
    assert b"test<br />\nbody" in response.data # assert body appears
    assert b'href="/1/update"' not in response.data #assert update button doesn't appear
    assert b'href="/create"' not in response.data

    auth.login(username="auth5",password="auth5") #login as auth5
    response = client.get("/")
    assert b'href="/create"' in response.data
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
    ("/image_upload",5)
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

def test_posts(client):
    response = client.get("/posts/1")
    assert b"test" in response.data


@pytest.mark.parametrize(("path","id"), (
    ("/create",3),
    ("/1/update",1),
))
def test_data_cleaning_input(client,auth, app,path,id):
    auth.login(username="auth5",password="auth5")
    client.post(path, data={"title":"<script>","body":"<script>"})

    with app.app_context():
        db= get_db()
        post = db.execute(f"SELECT * FROM post WHERE id={id}").fetchone()
        assert "<script>" not in post["title"]
        assert "<script>" not in post["body"]

@pytest.mark.parametrize("path",(
    "/",
    "/posts/3"
))
def test_data_cleaning_output(client,app,auth,path):
    auth.login(username="auth5",password="auth5")
    with app.app_context():
        db= get_db()
        db.execute("INSERT INTO post (title,body,author_id) VALUES (?,?,?)", ("<script></script>","<script></script>",2))
        db.commit()
    
    response = client.get(path)
    assert b"<script></script>" not in response.data
    assert b"<script></script>" not in response.data

def test_image_upload_page(client,auth):
    auth.login(username="auth5",password="auth5")
    response = client.get("/image_upload")
    assert b'<div id="div_1">' in response.data
    

def test_image_upload(client,auth, app):
    auth.login(username="auth5",password="auth5")
    response = client.post("/image_upload", data={"image_1":(io.BytesIO(b"Testing"), "testing.png"), "name_1":"testing","alt_1":"testing","image_2":(io.BytesIO(b""), "")}, content_type="multipart/form-data")
    assert b'<div class="flash">' not in response.data
    with app.app_context():
        db = get_db()
        db_response = db.execute("SELECT * FROM image WHERE id=2").fetchone()
        assert os.path.exists(os.path.join(app.config["IMAGE_UPLOAD"], "testing.png"))
        assert db_response["name"] == "testing.png"

def test_image_upload_multiple_inputs(client,auth,app):
    auth.login(username="auth5",password="auth5")
    response = client.post("/image_upload", data={"image_1":(io.BytesIO(b"Testing"), "testing.png"), "name_1":"test1","alt_1":"testing","image_2":(io.BytesIO(b"Testing"), "test2.png"), "name_2":"test2","alt_2":"test2","image_3":(io.BytesIO(b""), "")}, content_type="multipart/form-data")
    assert b'<div class="flash">' not in response.data
    with app.app_context():
        db = get_db()
        db_response = db.execute("SELECT count(id) FROM image").fetchone()
        assert db_response[0] == 3

@pytest.mark.parametrize(("payload","message"),(
        ({"image_1":(io.BytesIO(b"Test"), ""), "name_1":"testing","alt_1":"testing","image_2":(io.BytesIO(b""), "")},b"No file for upload 1."),
        ({"image_1":(io.BytesIO(b"testing"), "test2.pdf"), "name_1":"test2","alt_1":"testing","image_2":(io.BytesIO(b"Testing"), "test.png")},b"File extenstion pdf for upload 1 not allowed."),
        ({"image_1":(io.BytesIO(b"testing"), "test3.png"), "name_1":"","alt_1":"testing","image_2":(io.BytesIO(b""), "")},b"No name for upload 1."),
        ({"image_1":(io.BytesIO(b"Testing"), 'test.png'), "name_1":"test","alt_1":"testing","image_2":(io.BytesIO(b""), "")}, b"Upload 1 name test.png already exists."),
    )
)
def test_image_upload_value_inputs(client,auth,payload,message):
    auth.login(username="auth5",password="auth5")

    response = client.post("/image_upload", data=payload, content_type="multipart/form-data")
    print(response.data)
    assert message in response.data


def test_image_page(client):
    response = client.get("/image/1")
    assert response.data == b"testing data"


def test_image_gallery(client,auth):
    auth.login(username="auth5",password="auth5")
    response = client.get("/images")
    assert b"/image/1" in response.data

