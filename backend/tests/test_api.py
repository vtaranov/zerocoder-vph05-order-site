import os
os.environ["DATABASE_URL"] = "postgresql+psycopg://test:test@localhost/test"
os.environ["ADMIN_PASSWORD"] = "test-password"
from sqlalchemy import create_engine, event
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from app.core.database import Base, get_db
from sqlalchemy.orm import Session
from app.main import app

engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
@event.listens_for(engine, "connect")
def foreign_keys(conn, record): conn.execute("PRAGMA foreign_keys=ON")
Base.metadata.create_all(engine)
def database():
    with Session(engine) as session: yield session
app.dependency_overrides[get_db] = database
client = TestClient(app)
auth = ("admin", "test-password")
service = {"name":"Полировка", "description":"Блеск", "budget_min":10000, "budget_max":30000}

def test_complete_flow_and_validation():
    assert client.post("/api/admin/services", json=service).status_code == 401
    assert client.post("/api/admin/services", json=service, auth=("admin","wrong")).status_code == 401
    assert client.post("/api/admin/services", json={**service,"budget_max":1}, auth=auth).status_code == 422
    response = client.post("/api/admin/services", json=service, auth=auth)
    assert response.status_code == 201
    service_id = response.json()["id"]
    assert client.post("/api/admin/services", json=service, auth=auth).status_code == 409
    assert len(client.get("/api/services").json()) == 1
    data = {"service_id":service_id,"name":"Тестовый клиент","contact":"demo@example.com","budget":20000,"contact_method":"Email","consent":True,"metrics":{"time_on_page":35,"visits":2,"clicks":["submit"]}}
    for changed in [{"budget":1},{"service_id":999},{"consent":False},{"contact":"    "},{"metrics":{"time_on_page":-1}}]:
        assert client.post("/api/applications", json={**data,**changed}).status_code == 422
    assert client.get("/api/admin/applications", auth=auth).json() == []
    created = client.post("/api/applications", json=data)
    assert created.status_code == 201
    app_id = created.json()["id"]
    assert created.json()["message"] == "Заявка отправлена!"
    assert client.get("/api/admin/applications").status_code == 401
    assert client.get(f"/api/admin/applications/{app_id}/metrics").status_code == 401
    metrics = client.get(f"/api/admin/applications/{app_id}/metrics", auth=auth).json()
    assert metrics["visits"] == 2 and metrics["clicks"] == ["submit"]
    assert client.delete(f"/api/admin/services/{service_id}", auth=auth).status_code == 409
    assert client.delete(f"/api/admin/applications/{app_id}", auth=auth).status_code == 204
    assert client.get(f"/api/admin/applications/{app_id}/metrics", auth=auth).status_code == 404
    assert client.put(f"/api/admin/services/{service_id}", json={**service,"budget_max":40000},auth=auth).status_code == 200
    assert client.delete(f"/api/admin/services/{service_id}", auth=auth).status_code == 204
