from fastapi.testclient import TestClient

def test_create_task(auth_client):
    payload = {
            "title": "Test Task",
            "description": "This is a test task"
            }
    response = auth_client.post("/tasks", json=payload)
    response_data = response.json()

    assert response.status_code == 200
    assert "id" in response_data
    
def test_get_tasks(auth_client):
    payload1 = {
            "title": "Test Task 1",
            "description": "This is a test task 1"
            }
    payload2 = {
            "title": "Test Task 2",
            "description": "This is a test task 2"
            }
    auth_client.post("/tasks", json=payload1)
    auth_client.post("/tasks", json=payload2)

    response = auth_client.get("/tasks")
    response_data = response.json()

    assert response.status_code == 200
    assert response_data["total"] >= 2
    assert len(response_data["items"]) >= 2

def test_get_single_task(auth_client):
    payload = {
            "title": "Test Task",
            "description": "This is a test task"
            }
    task_id = auth_client.post("/tasks", json=payload).json()["id"]

    response = auth_client.get(f"/tasks/{task_id}")
    response_data = response.json()

    assert response.status_code == 200
    assert response_data["title"] == "Test Task"

def test_update_task(auth_client):
    payload = {
            "title": "Test Task",
            "description": "This is a test task"
            }
    task_id = auth_client.post("/tasks", json=payload).json()["id"]

    new_payload = {
        "description": "This is the updated task"
    }

    response = auth_client.put(f"/tasks/{task_id}", json=new_payload)
    response_data = response.json()

    assert response.status_code == 200
    assert response_data["description"] == "This is the updated task"

def test_delete_task(auth_client):
    payload = {
            "title": "Test Task",
            "description": "This is a test task"
            }
    task_id = auth_client.post("/tasks", json=payload).json()["id"]

    response = auth_client.delete(f"/tasks/{task_id}")
    assert response.status_code == 204

    response = auth_client.get(f"/tasks/{task_id}")
    assert response.status_code == 404

def test_cross_user_task_access(client: TestClient):
    registration_payload = {
            "email": "A@example.com",
            "password": "12345678"
            }
    client.post("/auth/register", json=registration_payload)

    login_payload = {
            "username": "A@example.com",
            "password": "12345678"
            }
    response = client.post("/auth/login", data=login_payload)
    
    payload = {
            "title": "Test Task",
            "description": "This is a test task"
            }
    
    token = response.json().get("access_token")
    client.headers.update({"Authorization": f"Bearer {token}"})

    response = client.post("/tasks", json=payload)
    response_data = response.json()
    task_id = response_data["id"]

    registration_payload = {
                "email": "B@example.com",
                "password": "12345678"
                }
    client.post("/auth/register", json=registration_payload)

    login_payload = {
            "username": "B@example.com",
            "password": "12345678"
            }
    
    response = client.post("/auth/login", data=login_payload)
    token = response.json().get("access_token")
    client.headers.update({"Authorization": f"Bearer {token}"})

    response = client.get(f"/tasks/{task_id}")

    assert response.status_code == 404