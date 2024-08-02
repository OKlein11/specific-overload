from overload import create_app

def test_config(): # Tests the factory config
    assert not create_app().testing
    assert create_app({"TESTING": True}).testing

def test_hello(client): # Tests the /hello endpoint
    response = client.get("/hello")
    assert response.data == b"Hello World"
