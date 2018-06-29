import pytest
import sqlite3
from datetime import datetime
from falcon import testing
from dynip import create_app
from stores import Store


class MockStore(Store):
    def __init__(self):
        self.ips = dict()

    def save(self, name, ip):
        self.ips[name] = {"ip": ip, "updated": datetime.utcnow().isoformat()}
        return self.ips[name]

    def load(self, name):
        return self.ips.get(name)


@pytest.fixture
def client():
    store = MockStore()
    app = create_app(store, None)
    return testing.TestClient(app)


def test_put(client: testing.TestClient):
    res = client.simulate_put("/foo")
    assert res.status_code == 200


def test_put_forwarded(client: testing.TestClient):
    xff = {"x-forwarded-for": "123.123.123.123"}
    client.simulate_put("/foo", headers=xff)

    res = client.simulate_get("/foo")
    assert res.text == "123.123.123.123"


def test_get(client: testing.TestClient):
    client.simulate_put("/foo")
    res = client.simulate_get("/foo")
    assert res.status_code == 200
    assert res.text == "127.0.0.1"
    assert res.headers["content-type"].startswith("text/plain")


def test_get_notfound(client: testing.TestClient):
    res = client.simulate_get("/foo")
    assert res.status_code == 404


def test_secret():
    store = MockStore()
    client = testing.TestClient(create_app(store, "seeecret"))

    xs = {"x-secret": "seeecret"}
    res = client.simulate_put("/foo", headers=xs)
    assert res.status_code == 200


def test_secret_invalid():
    store = MockStore()
    client = testing.TestClient(create_app(store, "seeecret"))

    xs = {"x-secret": "seeecret2"}
    res = client.simulate_put("/foo", headers=xs)
    assert res.status_code == 401


def test_case_insensitivity(client: testing.TestClient):
    client.simulate_put("/foo")
    res = client.simulate_get("/FOO")
    assert res.status_code == 200
    assert res.text == "127.0.0.1"


def test_empty_name(client: testing.TestClient):
    res = client.simulate_put("/")
    assert res.status_code == 400
