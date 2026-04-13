from sqlalchemy import text


def _create_capture(client, auth_headers, payload=None):
    response = client.post(
        "/api/v1/contacts-capture",
        headers=auth_headers,
        json=payload
        or {
            "origin": "MOBILE",
            "classification": "CIDADAO",
            "full_name": "Maria da Silva",
            "district": "Centro",
        },
    )
    assert response.status_code == 201
    return response.json()


def test_create_capture_requires_auth(client):
    response = client.post(
        "/api/v1/contacts-capture",
        json={
            "origin": "MOBILE",
            "classification": "CIDADAO",
            "full_name": "Maria da Silva",
        },
    )
    assert response.status_code in (401, 403)


def test_create_capture_persists_and_audits(client, auth_headers, db_session):
    body = _create_capture(client, auth_headers)
    assert body["origin"] == "MOBILE"
    assert body["capture_status"] == "NEW"

    capture_count = db_session.execute(text("select count(*) from territory.contacts_capture")).scalar_one()
    audit_count = db_session.execute(
        text(
            """
            select count(*)
            from governance.audit_logs
            where entity_schema = 'territory'
              and entity_name = 'contacts_capture'
              and action = 'CREATE'
            """
        )
    ).scalar_one()

    assert capture_count == 1
    assert audit_count == 1


def test_classify_capture_updates_status_and_audits(client, auth_headers, db_session):
    capture = _create_capture(client, auth_headers)

    response = client.post(
        f"/api/v1/contacts-capture/{capture['id']}/classify",
        headers=auth_headers,
        json={
            "classification": "DEMANDA",
            "priority_level": "HIGH",
            "notes": "Solicitacao prioritaria",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["classification"] == "DEMANDA"
    assert body["priority_level"] == "HIGH"
    assert body["capture_status"] == "CLASSIFIED"

    audit_count = db_session.execute(
        text(
            """
            select count(*)
            from governance.audit_logs
            where entity_schema = 'territory'
              and entity_name = 'contacts_capture'
              and action = 'UPDATE'
            """
        )
    ).scalar_one()

    assert audit_count == 1


def test_convert_capture_to_demand_creates_master_person_and_audits(client, auth_headers, db_session):
    capture = _create_capture(
        client,
        auth_headers,
        {
            "origin": "MOBILE",
            "classification": "DEMANDA",
            "full_name": "Joao Territorio",
            "phone": "11970000000",
            "district": "Vila Revisa",
            "notes": "Precisa de acompanhamento",
            "latitude": -23.5505,
            "longitude": -46.6333,
        },
    )

    response = client.post(
        f"/api/v1/contacts-capture/{capture['id']}/convert-demand",
        headers=auth_headers,
        json={
            "category": "SAUDE",
            "title": "Acompanhamento de saude",
            "priority": "HIGH",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["created_person"] is True
    assert body["capture"]["capture_status"] == "CONVERTED_TO_DEMAND"
    assert body["person"]["full_name"] == "Joao Territorio"
    assert body["person"]["phone"] == "11970000000"
    assert body["demand"]["capture_id"] == capture["id"]
    assert body["demand"]["category"] == "SAUDE"
    assert body["demand"]["status"] == "OPEN"
    assert body["address"]["district"] == "Vila Revisa"

    demands = client.get("/api/v1/demands", headers=auth_headers)
    assert demands.status_code == 200
    assert [item["id"] for item in demands.json()] == [body["demand"]["id"]]

    counts = db_session.execute(
        text(
            """
            select
                (select count(*) from core.persons) as persons,
                (select count(*) from core.addresses) as addresses,
                (select count(*) from territory.demands) as demands,
                (
                    select count(*)
                    from territory.contacts_capture
                    where person_id is not null
                      and capture_status = 'CONVERTED_TO_DEMAND'
                ) as converted_captures
            """
        )
    ).one()
    assert counts.persons == 1
    assert counts.addresses == 1
    assert counts.demands == 1
    assert counts.converted_captures == 1

    audit_rows = db_session.execute(
        text(
            """
            select entity_schema, entity_name, action, count(*) as total
            from governance.audit_logs
            where (entity_schema, entity_name, action) in (
                ('core', 'persons', 'CREATE'),
                ('core', 'addresses', 'CREATE'),
                ('territory', 'demands', 'CREATE'),
                ('territory', 'contacts_capture', 'CONVERT')
            )
            group by entity_schema, entity_name, action
            """
        )
    ).all()

    assert {(row.entity_schema, row.entity_name, row.action): row.total for row in audit_rows} == {
        ("core", "persons", "CREATE"): 1,
        ("core", "addresses", "CREATE"): 1,
        ("territory", "demands", "CREATE"): 1,
        ("territory", "contacts_capture", "CONVERT"): 1,
    }
