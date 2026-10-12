def test_root_and_health_endpoints(client):
    root = client.get("/")
    assert root.status_code == 200
    assert root.json() == {"message": "Secure REST API", "version": "1.0.0", "docs": "/docs"}

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json() == {"status": "healthy"}


def test_register_user_returns_public_fields(client):
    response = client.post(
        "/auth/register",
        json={"username": "alice", "email": "alice@example.com", "password": "correct horse"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["username"] == "alice"
    assert body["email"] == "alice@example.com"
    assert isinstance(body["id"], int)
    assert "created_at" in body
    assert "hashed_password" not in body


def test_register_rejects_duplicate_username_or_email(client, registered_user):
    duplicate_username = client.post(
        "/auth/register",
        json={"username": registered_user["username"], "email": "other@example.com", "password": "password123"},
    )
    duplicate_email = client.post(
        "/auth/register",
        json={"username": "bob", "email": registered_user["email"], "password": "password123"},
    )

    assert duplicate_username.status_code == 400
    assert duplicate_email.status_code == 400


def test_register_validates_request_body(client):
    response = client.post(
        "/auth/register",
        json={"username": "a", "email": "not-an-email", "password": "short"},
    )
    assert response.status_code == 422


def test_login_returns_bearer_token(client, registered_user):
    response = client.post(
        "/auth/login", json={"username": "alice", "password": "correct horse"}
    )
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]


def test_login_rejects_wrong_credentials(client, registered_user):
    response = client.post(
        "/auth/login", json={"username": "alice", "password": "wrong password"}
    )
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_users_endpoint_requires_authentication(client):
    response = client.get("/api/data")
    assert response.status_code == 403


def test_users_endpoint_lists_registered_users(client, auth_headers, registered_user):
    response = client.get("/api/data", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["username"] == "alice"


def test_posts_endpoints_crud_and_authorization(client, auth_headers):
    created = client.post(
        "/api/posts/",
        headers=auth_headers,
        json={"title": "Hello", "content": "Post body"},
    )
    assert created.status_code == 201
    post = created.json()
    assert post["title"] == "Hello"
    assert post["content"] == "Post body"

    listed = client.get("/api/posts/", headers=auth_headers)
    assert listed.status_code == 200
    assert [item["id"] for item in listed.json()] == [post["id"]]

    fetched = client.get(f"/api/posts/{post['id']}", headers=auth_headers)
    assert fetched.status_code == 200
    assert fetched.json() == post

    deleted = client.delete(f"/api/posts/{post['id']}", headers=auth_headers)
    assert deleted.status_code == 204
    assert deleted.content == b""
    assert client.get(f"/api/posts/{post['id']}", headers=auth_headers).status_code == 404


def test_post_endpoints_require_authentication(client):
    assert client.get("/api/posts/").status_code == 403
    assert client.post("/api/posts/", json={"title": "Hi", "content": "Body"}).status_code == 403


def test_post_creation_validates_body(client, auth_headers):
    response = client.post(
        "/api/posts/", headers=auth_headers, json={"title": "", "content": "Body"}
    )
    assert response.status_code == 422


def test_get_missing_post_returns_404(client, auth_headers):
    response = client.get("/api/posts/999", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"


def test_only_author_can_delete_post(client, auth_headers):
    created = client.post(
        "/api/posts/", headers=auth_headers, json={"title": "Mine", "content": "Body"}
    ).json()

    client.post(
        "/auth/register",
        json={"username": "bob", "email": "bob@example.com", "password": "correct horse"},
    )
    token = client.post(
        "/auth/login", json={"username": "bob", "password": "correct horse"}
    ).json()["access_token"]

    response = client.delete(
        f"/api/posts/{created['id']}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403
    assert client.get(f"/api/posts/{created['id']}", headers=auth_headers).status_code == 200


def test_delete_missing_post_returns_404(client, auth_headers):
    response = client.delete("/api/posts/999", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"
