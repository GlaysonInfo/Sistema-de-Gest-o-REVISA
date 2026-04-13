from uuid import uuid4

from sqlalchemy import text


def _create_organization(db_session, name="Mandato Teste"):
    organization_id = uuid4()
    db_session.execute(
        text(
            """
            insert into core.organizations (id, type, name)
            values (cast(:id as uuid), 'MANDATO', :name)
            """
        ),
        {"id": str(organization_id), "name": name},
    )
    db_session.commit()
    return organization_id


def test_mobile_intake_registers_polo_beneficiary_end_to_end(client, auth_headers):
    demo = client.post("/api/v1/demo/bootstrap", headers=auth_headers)
    assert demo.status_code == 200
    demo_body = demo.json()

    response = client.post(
        "/api/v1/mobile/intakes",
        headers=auth_headers,
        json={
            "intake_type": "POLO_BENEFICIARIO",
            "full_name": "Beneficiario Mobile",
            "phone": "11977770001",
            "district": "Jardim Mobile",
            "notes": "Captado pelo aplicativo mobile",
            "priority_level": "HIGH",
            "organization_id": demo_body["organization"]["id"],
            "polo_id": demo_body["polo"]["id"],
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["capture"]["origin"] == "MOBILE"
    assert body["capture"]["classification"] == "BENEFICIARIO"
    assert body["person"]["full_name"] == "Beneficiario Mobile"
    assert body["demand"]["category"] == "POLO_BENEFICIARIO"
    assert body["beneficiary"]["polo_id"] == demo_body["polo"]["id"]
    assert body["created_person"] is True
    assert body["created_beneficiary"] is True

    timeline = client.get(f"/api/v1/persons/{body['person']['id']}/timeline", headers=auth_headers)
    assert timeline.status_code == 200
    timeline_types = {item["type"] for item in timeline.json()["items"]}
    assert {"CAPTACAO", "DEMANDA", "BENEFICIARIO_POLO"}.issubset(timeline_types)


def test_mobile_intake_registers_mandate_follow_up_in_macro(client, auth_headers, db_session):
    organization_id = _create_organization(db_session)

    response = client.post(
        "/api/v1/mobile/intakes",
        headers=auth_headers,
        json={
            "intake_type": "MANDATO_ACOMPANHAMENTO",
            "full_name": "Pessoa Mandato Mobile",
            "phone": "11977770002",
            "district": "Centro",
            "notes": "Pessoa cadastrada pela equipe do mandato",
            "priority_level": "MEDIUM",
            "organization_id": str(organization_id),
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["capture"]["origin"] == "MOBILE"
    assert body["capture"]["classification"] == "ACOMPANHAMENTO"
    assert body["demand"]["category"] == "ACOMPANHAMENTO_MANDATO"
    assert body["person_link"]["organization_id"] == str(organization_id)
    assert body["person_link"]["link_type"] == "MANDATO_ACOMPANHAMENTO"
    assert body["created_person_link"] is True

    rows = db_session.execute(
        text(
            """
            select entity_schema, entity_name, action
            from governance.audit_logs
            where new_values_json::text like '%mobile_intake%'
            """
        )
    ).all()
    assert ("territory", "contacts_capture", "CREATE") in rows
    assert ("territory", "demands", "CREATE") in rows
    assert ("core", "person_links", "CREATE") in rows
