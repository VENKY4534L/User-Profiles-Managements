import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pytest
from app import create_app, db
from app.models import User

@pytest.fixture()
def app():
    app = create_app({"TESTING": True, "SECRET_KEY": "test-key",
                      "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture()
def client(app):
    return app.test_client()

def payload(email="asha@example.com", name="Asha Rao"):
    return {"name": name, "email": email, "role": "Developer", "password": "demo-password-123"}

def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "ok"

def test_create_and_list(client):
    response = client.post("/api/users", json=payload())
    assert response.status_code == 201
    assert response.json["email"] == "asha@example.com"
    assert "password" not in response.json
    assert client.get("/api/users").json["count"] == 1

def test_password_is_hashed(app, client):
    client.post("/api/users", json=payload())
    with app.app_context():
        user = User.query.filter_by(email="asha@example.com").first()
        assert user.password_hash != "demo-password-123"

def test_invalid_payload(client):
    response = client.post("/api/users", json={"name": "", "email": "bad", "role": "User", "password": "short"})
    assert response.status_code == 400
    assert "errors" in response.json

def test_update(client):
    user_id = client.post("/api/users", json=payload()).json["id"]
    response = client.patch(f"/api/users/{user_id}", json={"name": "Asha Updated", "email": "asha@example.com", "role": "Manager"})
    assert response.status_code == 200
    assert response.json["name"] == "Asha Updated"

def test_delete(client):
    user_id = client.post("/api/users", json=payload()).json["id"]
    assert client.delete(f"/api/users/{user_id}").status_code == 200
    assert client.get(f"/api/users/{user_id}").status_code == 404

def test_duplicate_email(client):
    client.post("/api/users", json=payload())
    response = client.post("/api/users", json=payload(name="Another Person"))
    assert response.status_code == 400
    assert "email" in response.json["errors"]
