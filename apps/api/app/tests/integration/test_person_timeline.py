def test_person_timeline_returns_operational_journey(client, auth_headers):
    bootstrap = client.post("/api/v1/demo/bootstrap", headers=auth_headers)
    assert bootstrap.status_code == 200
    person_id = bootstrap.json()["person"]["id"]

    summary_response = client.get(f"/api/v1/persons/{person_id}/operational-summary", headers=auth_headers)
    assert summary_response.status_code == 200
    summary = summary_response.json()
    assert summary["person"]["id"] == person_id
    assert summary["current_polo"]["id"] == bootstrap.json()["polo"]["id"]
    assert summary["beneficiary_status"] == "ATIVO"
    assert summary["open_demands"] == 1
    assert summary["open_tasks"] == 1
    assert summary["last_attendance_at"]
    assert summary["last_occurrence"]["title"] == "Ocorrencia de demo"
    assert summary["journey_status"] == "EM_ACOMPANHAMENTO"

    timeline_response = client.get(f"/api/v1/persons/{person_id}/timeline", headers=auth_headers)
    assert timeline_response.status_code == 200
    timeline = timeline_response.json()
    assert timeline["person"]["id"] == person_id
    assert timeline["summary"]["journey_status"] == "EM_ACOMPANHAMENTO"

    item_types = {item["type"] for item in timeline["items"]}
    assert {
        "CAPTACAO",
        "DEMANDA",
        "TAREFA",
        "BENEFICIARIO_POLO",
        "FREQUENCIA",
        "OCORRENCIA",
    }.issubset(item_types)

    occurrences = [item for item in timeline["items"] if item["type"] == "OCORRENCIA"]
    assert occurrences[0]["metadata_json"]["severity"] == "MEDIUM"
