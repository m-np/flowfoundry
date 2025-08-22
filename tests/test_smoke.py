from flowfoundry import ping
from flowfoundry.hello import hello

def test_ping():
    assert ping() == "flowfoundry: ok"

def test_hello():
    assert hello("dev") == "hello, dev!"