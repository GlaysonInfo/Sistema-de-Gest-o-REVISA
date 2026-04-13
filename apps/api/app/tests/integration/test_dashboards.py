def test_dashboard_requires_auth(client):
    response = client.get("/api/v1/vereadores/11111111-1111-1111-1111-111111111111/dashboard")
    assert response.status_code in (401, 403)
