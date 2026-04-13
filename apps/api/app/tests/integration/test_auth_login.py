def test_login_success(client, admin_user):
    response = client.post(
        "/api/v1/auth/login",
        json={"username": admin_user.username, "password": "Admin@123"},
    )

    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "Bearer"


def test_me_returns_admin_context(client, auth_headers):
    response = client.get("/api/v1/auth/me", headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["username"] == "admin"
    assert "ADM_GERAL_REVISA" in body["roles"]
