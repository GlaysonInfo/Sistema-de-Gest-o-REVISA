def test_relationship_expansion_layer_registers_classification_leadership_partner_and_event(client, auth_headers):
    demo = client.post("/api/v1/demo/bootstrap", headers=auth_headers)
    assert demo.status_code == 200
    demo_body = demo.json()

    intake = client.post(
        "/api/v1/mobile/intakes",
        headers=auth_headers,
        json={
            "intake_type": "MANDATO_ACOMPANHAMENTO",
            "full_name": "Lideranca Vila Cristina",
            "phone": "11973330001",
            "district": "Vila Cristina",
            "notes": "Pessoa forte no bairro",
            "organization_id": demo_body["organization"]["id"],
        },
    )
    assert intake.status_code == 201
    person_id = intake.json()["person"]["id"]

    classification = client.post(
        "/api/v1/relationships/classifications",
        headers=auth_headers,
        json={
            "person_id": person_id,
            "organization_id": demo_body["organization"]["id"],
            "level": "LIDERANCA",
            "influence": "ALTA",
            "engagement": "FORTE",
            "vote_2028": "VOTO_CERTO",
            "priority": "HIGH",
            "notes": "Classificacao interna restrita",
        },
    )
    assert classification.status_code == 201
    assert classification.json()["level"] == "LIDERANCA"

    leadership = client.post(
        "/api/v1/relationships/leaderships",
        headers=auth_headers,
        json={
            "person_id": person_id,
            "organization_id": demo_body["organization"]["id"],
            "polo_id": demo_body["polo"]["id"],
            "district": "Vila Cristina",
            "leadership_type": "COMUNITARIA",
            "area_atuacao": "REVIVA BETIM",
            "influence_count": 80,
            "loyalty_level": "FORTE",
            "notes": "Possivel lideranca principal",
        },
    )
    assert leadership.status_code == 201
    assert leadership.json()["district"] == "Vila Cristina"

    partner = client.post(
        "/api/v1/relationships/partners",
        headers=auth_headers,
        json={
            "organization_id": demo_body["organization"]["id"],
            "name": "Igreja Parceira Vila Cristina",
            "partner_type": "IGREJA",
            "contact_name": "Responsavel Local",
            "contact_phone": "31999990000",
            "district": "Vila Cristina",
            "contribution_area": "ESPACO",
            "service_offered": "Espaco para evento de entrada",
            "partnership_type": "ESPACO",
            "status": "ACTIVE",
        },
    )
    assert partner.status_code == 201
    assert partner.json()["partner_type"] == "IGREJA"

    event = client.post(
        "/api/v1/relationships/field-events",
        headers=auth_headers,
        json={
            "organization_id": demo_body["organization"]["id"],
            "polo_id": demo_body["polo"]["id"],
            "partner_id": partner.json()["id"],
            "title": "REVIVA BETIM - Vila Cristina",
            "district": "Vila Cristina",
            "event_type": "ACAO_SOCIAL",
            "event_date": "2026-04-11",
            "status": "PLANNED",
            "expected_people": 120,
            "captures_count": 0,
            "leaders_identified": 1,
            "next_action": "Criar grupo WhatsApp e iniciar atividade fixa",
        },
    )
    assert event.status_code == 201
    assert event.json()["expected_people"] == 120

    classified = client.get(
        "/api/v1/relationships/classifications",
        headers=auth_headers,
        params={"person_id": person_id},
    )
    assert classified.status_code == 200
    assert [item["level"] for item in classified.json()] == ["LIDERANCA"]

    leaderships = client.get(
        "/api/v1/relationships/leaderships",
        headers=auth_headers,
        params={"district": "Vila Cristina", "active": True},
    )
    assert leaderships.status_code == 200
    assert [item["person_id"] for item in leaderships.json()] == [person_id]
