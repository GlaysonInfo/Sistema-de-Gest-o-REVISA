def test_polo_overview_consolidates_beneficiaries_attendance_occurrences_and_events(client, auth_headers):
    demo = client.post("/api/v1/demo/bootstrap", headers=auth_headers)
    assert demo.status_code == 200
    demo_body = demo.json()
    polo_id = demo_body["polo"]["id"]

    event = client.post(
        "/api/v1/relationships/field-events",
        headers=auth_headers,
        json={
            "organization_id": demo_body["organization"]["id"],
            "polo_id": polo_id,
            "title": "Aula aberta REVIVA BETIM",
            "district": "Centro",
            "event_type": "AULA_ABERTA",
            "event_date": "2026-04-11",
            "status": "PLANNED",
            "expected_people": 80,
            "captures_count": 10,
            "leaders_identified": 1,
        },
    )
    assert event.status_code == 201

    overview = client.get(f"/api/v1/polos/{polo_id}/overview", headers=auth_headers)
    assert overview.status_code == 200
    body = overview.json()

    assert body["polo"]["id"] == polo_id
    assert body["metrics"]["total_beneficiarios"] == 1
    assert body["metrics"]["active_beneficiarios"] == 1
    assert body["metrics"]["attendance_records"] == 1
    assert body["metrics"]["present_records"] == 1
    assert body["metrics"]["open_occurrences"] == 1
    assert body["metrics"]["planned_events"] == 1
    assert body["beneficiaries"][0]["id"] == demo_body["beneficiary"]["id"]
    assert body["recent_attendances"][0]["id"] == demo_body["attendance"]["id"]
    assert body["recent_occurrences"][0]["id"] == demo_body["occurrence"]["id"]
    assert body["field_events"][0]["id"] == event.json()["id"]
