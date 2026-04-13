from uuid import uuid4

from sqlalchemy import text


def _create_person(client, auth_headers, payload=None):
    response = client.post(
        "/api/v1/persons",
        headers=auth_headers,
        json=payload or {"full_name": "Teste de Cutover", "phone": "11999999999"},
    )
    assert response.status_code == 201
    return response.json()


def test_list_persons_requires_auth(client):
    response = client.get("/api/v1/persons")
    assert response.status_code in (401, 403)


def test_create_person_persists_and_audits(client, auth_headers, db_session):
    response = client.post(
        "/api/v1/persons",
        headers=auth_headers,
        json={"full_name": "Teste de Cutover", "phone": "11999999999"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["full_name"] == "Teste de Cutover"

    person_count = db_session.execute(text("select count(*) from core.persons")).scalar_one()
    audit_count = db_session.execute(
        text(
            """
            select count(*)
            from governance.audit_logs
            where entity_schema = 'core'
              and entity_name = 'persons'
              and action = 'CREATE'
            """
        )
    ).scalar_one()

    assert person_count == 1
    assert audit_count == 1


def test_get_update_and_search_person(client, auth_headers, db_session):
    first = _create_person(
        client,
        auth_headers,
        {
            "full_name": "Ana Revisa",
            "cpf": "11122233344",
            "phone": "11911112222",
            "email": "ana@example.test",
        },
    )
    _create_person(
        client,
        auth_headers,
        {
            "full_name": "Bruno Campo",
            "cpf": "55566677788",
            "phone": "11933334444",
        },
    )

    detail = client.get(f"/api/v1/persons/{first['id']}", headers=auth_headers)
    assert detail.status_code == 200
    assert detail.json()["cpf"] == "11122233344"

    update = client.patch(
        f"/api/v1/persons/{first['id']}",
        headers=auth_headers,
        json={"phone": "11988887777", "notes": "Cadastro revisado"},
    )
    assert update.status_code == 200
    assert update.json()["phone"] == "11988887777"
    assert update.json()["notes"] == "Cadastro revisado"

    search = client.get("/api/v1/persons", headers=auth_headers, params={"search": "Ana"})
    assert search.status_code == 200
    assert [person["full_name"] for person in search.json()] == ["Ana Revisa"]

    phone_search = client.get("/api/v1/persons", headers=auth_headers, params={"phone": "11988887777"})
    assert phone_search.status_code == 200
    assert [person["id"] for person in phone_search.json()] == [first["id"]]

    missing = client.get(f"/api/v1/persons/{uuid4()}", headers=auth_headers)
    assert missing.status_code == 404

    audit_count = db_session.execute(
        text(
            """
            select count(*)
            from governance.audit_logs
            where entity_schema = 'core'
              and entity_name = 'persons'
              and action = 'UPDATE'
            """
        )
    ).scalar_one()

    assert audit_count == 1


def test_person_address_consent_and_link_flow_persists_and_audits(client, auth_headers, db_session):
    person = _create_person(
        client,
        auth_headers,
        {
            "full_name": "Carla Territorial",
            "phone": "21999990000",
        },
    )

    address = client.post(
        f"/api/v1/persons/{person['id']}/addresses",
        headers=auth_headers,
        json={
            "label": "Casa",
            "street": "Rua Um",
            "number": "123",
            "district": "Centro",
            "city": "Sao Paulo",
            "state": "SP",
            "zip_code": "01001000",
            "latitude": -23.5505,
            "longitude": -46.6333,
        },
    )
    assert address.status_code == 201
    assert address.json()["person_id"] == person["id"]
    assert address.json()["city"] == "Sao Paulo"

    addresses = client.get(f"/api/v1/persons/{person['id']}/addresses", headers=auth_headers)
    assert addresses.status_code == 200
    assert len(addresses.json()) == 1

    consent = client.post(
        f"/api/v1/persons/{person['id']}/consents",
        headers=auth_headers,
        json={
            "consent_type": "LGPD_CONTACT",
            "granted": True,
            "version": "v1",
            "evidence_ref": "captura:mobile",
        },
    )
    assert consent.status_code == 201
    assert consent.json()["granted"] is True
    assert consent.json()["granted_at"] is not None

    consents = client.get(f"/api/v1/persons/{person['id']}/consents", headers=auth_headers)
    assert consents.status_code == 200
    assert [item["consent_type"] for item in consents.json()] == ["LGPD_CONTACT"]

    link = client.post(
        f"/api/v1/persons/{person['id']}/links",
        headers=auth_headers,
        json={"link_type": "APOIADOR", "metadata_json": {"source": "test"}},
    )
    assert link.status_code == 201
    assert link.json()["link_type"] == "APOIADOR"
    assert link.json()["metadata_json"] == {"source": "test"}

    links = client.get(f"/api/v1/persons/{person['id']}/links", headers=auth_headers)
    assert links.status_code == 200
    assert len(links.json()) == 1

    audit_rows = db_session.execute(
        text(
            """
            select entity_name, count(*) as total
            from governance.audit_logs
            where entity_schema = 'core'
              and action = 'CREATE'
              and entity_name in ('addresses', 'consents', 'person_links')
            group by entity_name
            """
        )
    ).all()

    assert {row.entity_name: row.total for row in audit_rows} == {
        "addresses": 1,
        "consents": 1,
        "person_links": 1,
    }
