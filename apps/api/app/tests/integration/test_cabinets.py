def test_cabinet_overview_consolidates_vereador_operation(client, auth_headers):
    demo = client.post("/api/v1/demo/bootstrap", headers=auth_headers)
    assert demo.status_code == 200
    demo_body = demo.json()

    cabinets = client.get("/api/v1/cabinets", headers=auth_headers)
    assert cabinets.status_code == 200
    assert [item["organization"]["id"] for item in cabinets.json()] == [demo_body["cabinet"]["id"]]

    overview = client.get(
        f"/api/v1/cabinets/{demo_body['cabinet']['id']}/overview",
        headers=auth_headers,
    )
    assert overview.status_code == 200
    body = overview.json()

    assert body["cabinet"]["organization"]["name"] == "Gabinete Demo REVISA"
    assert body["cabinet"]["vereador"]["id"] == demo_body["vereador"]["id"]
    assert body["cabinet"]["vereador"]["person"]["full_name"] == "Vereador Demo"
    assert body["metrics"]["captures"] == 1
    assert body["metrics"]["demands"] == 1
    assert body["metrics"]["open_demands"] == 1
    assert body["metrics"]["tasks"] == 1
    assert body["metrics"]["open_tasks"] == 1
    assert body["recent_captures"][0]["id"] == demo_body["capture"]["id"]
    assert body["recent_demands"][0]["id"] == demo_body["demand"]["id"]
    assert body["recent_tasks"][0]["id"] == demo_body["task"]["id"]


def test_create_cabinet_registers_organization_and_vereador(client, auth_headers):
    response = client.post(
        "/api/v1/cabinets",
        headers=auth_headers,
        json={
            "name": "Gabinete Norte",
            "legal_name": "Gabinete Norte",
            "document_number": "GAB-NORTE",
            "vereador_full_name": "Ana Vereadora",
            "vereador_phone": "11970000001",
            "vereador_email": "ana.vereador@revisa.local",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["organization"]["type"] == "GABINETE"
    assert body["organization"]["name"] == "Gabinete Norte"
    assert body["vereador"]["person"]["full_name"] == "Ana Vereadora"
