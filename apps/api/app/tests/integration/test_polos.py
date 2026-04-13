from uuid import uuid4

from sqlalchemy import text


def _create_organization(db_session):
    organization_id = uuid4()
    db_session.execute(
        text(
            """
            insert into core.organizations (id, type, name)
            values (cast(:id as uuid), 'POLO', 'Polo Teste')
            """
        ),
        {"id": str(organization_id)},
    )
    return organization_id


def _create_cabinet(client, auth_headers):
    response = client.post(
        "/api/v1/cabinets",
        headers=auth_headers,
        json={
            "name": "Gabinete Polo Teste",
            "document_number": "GAB-POLO-TESTE",
            "vereador_full_name": "Vereador Polo Teste",
            "vereador_phone": "11955550001",
        },
    )
    assert response.status_code == 201
    return response.json()


def _create_person(client, auth_headers):
    response = client.post(
        "/api/v1/persons",
        headers=auth_headers,
        json={"full_name": "Beneficiario Polo", "phone": "11955550000"},
    )
    assert response.status_code == 201
    return response.json()


def _create_capture(client, auth_headers):
    response = client.post(
        "/api/v1/contacts-capture",
        headers=auth_headers,
        json={
            "origin": "MOBILE",
            "classification": "BENEFICIARIO",
            "full_name": "Beneficiario Polo",
            "phone": "11955550000",
        },
    )
    assert response.status_code == 201
    return response.json()


def _create_polo(client, auth_headers, organization_id, vereador_id):
    response = client.post(
        "/api/v1/polos",
        headers=auth_headers,
        json={
            "organization_id": str(organization_id),
            "vereador_id": vereador_id,
            "code": "POLO-01",
            "address_label": "Endereco inicial",
        },
    )
    assert response.status_code == 201
    return response.json()


def _create_beneficiario(client, auth_headers, polo_id, person_id, capture_id):
    response = client.post(
        f"/api/v1/polos/{polo_id}/beneficiarios",
        headers=auth_headers,
        json={
            "person_id": person_id,
            "source_capture_id": capture_id,
            "status": "PRE_CADASTRADO",
        },
    )
    assert response.status_code == 201
    return response.json()


def _create_modalidade(client, auth_headers, polo_id):
    response = client.post(
        f"/api/v1/polos/{polo_id}/modalidades",
        headers=auth_headers,
        json={
            "name": "Futebol",
            "description": "Turma de futebol do polo",
            "active": True,
        },
    )
    assert response.status_code == 201
    return response.json()


def test_list_beneficiarios_requires_auth(client):
    response = client.get("/api/v1/polos/11111111-1111-1111-1111-111111111111/beneficiarios")
    assert response.status_code in (401, 403)


def test_polo_beneficiary_attendance_and_occurrence_flow(client, auth_headers, db_session):
    organization_id = _create_organization(db_session)
    cabinet = _create_cabinet(client, auth_headers)
    person = _create_person(client, auth_headers)
    capture = _create_capture(client, auth_headers)
    polo = _create_polo(client, auth_headers, organization_id, cabinet["vereador"]["id"])

    polo_detail = client.get(f"/api/v1/polos/{polo['id']}", headers=auth_headers)
    assert polo_detail.status_code == 200
    assert polo_detail.json()["code"] == "POLO-01"

    duplicate_polo = client.post(
        "/api/v1/polos",
        headers=auth_headers,
        json={
            "organization_id": str(organization_id),
            "vereador_id": cabinet["vereador"]["id"],
            "code": "POLO-01",
            "address_label": "Endereco inicial",
        },
    )
    assert duplicate_polo.status_code == 409
    assert duplicate_polo.json()["detail"] == "Polo ja existe para esta organizacao"

    polo_update = client.patch(
        f"/api/v1/polos/{polo['id']}",
        headers=auth_headers,
        json={"address_label": "Endereco revisado"},
    )
    assert polo_update.status_code == 200
    assert polo_update.json()["address_label"] == "Endereco revisado"

    beneficiario = _create_beneficiario(client, auth_headers, polo["id"], person["id"], capture["id"])
    assert beneficiario["polo_id"] == polo["id"]
    assert beneficiario["person_id"] == person["id"]
    assert beneficiario["source_capture_id"] == capture["id"]

    beneficiario_detail = client.get(
        f"/api/v1/polos/{polo['id']}/beneficiarios/{beneficiario['id']}",
        headers=auth_headers,
    )
    assert beneficiario_detail.status_code == 200

    beneficiario_update = client.patch(
        f"/api/v1/polos/{polo['id']}/beneficiarios/{beneficiario['id']}",
        headers=auth_headers,
        json={"status": "ATIVO"},
    )
    assert beneficiario_update.status_code == 200
    assert beneficiario_update.json()["status"] == "ATIVO"

    modalidade = _create_modalidade(client, auth_headers, polo["id"])
    assert modalidade["polo_id"] == polo["id"]
    assert modalidade["name"] == "Futebol"
    assert modalidade["active"] is True

    action_plan = client.post(
        f"/api/v1/polos/{polo['id']}/modalidades/{modalidade['id']}/action-plans",
        headers=auth_headers,
        data={
            "base_year": "2026",
            "title": "Plano de Acao Futebol - Ano Base 2026",
            "professional_name": "Professor Futebol",
            "notes": "Plano anual entregue ao administrador do Polo.",
        },
        files={"file": ("plano-acao-futebol.txt", b"plano de acao 2026", "text/plain")},
    )
    assert action_plan.status_code == 201
    assert action_plan.json()["base_year"] == 2026
    assert action_plan.json()["modalidade_id"] == modalidade["id"]
    assert action_plan.json()["original_filename"] == "plano-acao-futebol.txt"

    action_plan_list = client.get(
        f"/api/v1/polos/{polo['id']}/action-plans",
        headers=auth_headers,
        params={"base_year": 2026},
    )
    assert action_plan_list.status_code == 200
    assert [item["id"] for item in action_plan_list.json()] == [action_plan.json()["id"]]

    modalidade_update = client.patch(
        f"/api/v1/polos/{polo['id']}/modalidades/{modalidade['id']}",
        headers=auth_headers,
        json={"description": "Turma revisada", "active": False},
    )
    assert modalidade_update.status_code == 200
    assert modalidade_update.json()["description"] == "Turma revisada"
    assert modalidade_update.json()["active"] is False

    modalidade_list = client.get(
        f"/api/v1/polos/{polo['id']}/modalidades",
        headers=auth_headers,
    )
    assert modalidade_list.status_code == 200
    assert [item["id"] for item in modalidade_list.json()] == [modalidade["id"]]

    monthly_payload = {
        "reference_month": "2026-04-01",
        "occurrence_summary": "No dia 21 as atividades de quadra nao foram realizadas devido chuva.",
        "notes": "Relatorio conferido pelo administrador do Polo.",
        "modalities": [
            {
                "modalidade_id": modalidade["id"],
                "modalidade_name": "Futebol",
                "active": True,
                "beneficiaries_count": 25,
                "notes": "Atividades regulares no mes.",
            }
        ],
    }
    monthly_preview = client.post(
        f"/api/v1/polos/{polo['id']}/monthly-reports/preview",
        headers=auth_headers,
        json=monthly_payload,
    )
    assert monthly_preview.status_code == 200
    assert "RELATORIO MENSAL" in monthly_preview.json()["narrative_text"]
    assert monthly_preview.json()["active_modalities_count"] == 1

    monthly_report = client.post(
        f"/api/v1/polos/{polo['id']}/monthly-reports",
        headers=auth_headers,
        json={**monthly_payload, "narrative_text": monthly_preview.json()["narrative_text"]},
    )
    assert monthly_report.status_code == 201
    assert monthly_report.json()["total_beneficiaries"] == 25

    monthly_upload = client.post(
        f"/api/v1/polos/{polo['id']}/monthly-reports/{monthly_report.json()['id']}/attachments",
        headers=auth_headers,
        data={"attachment_type": "ATTENDANCE_LIST", "description": "Lista de presenca do futebol"},
        files={"files": ("lista-presenca.txt", b"presenca", "text/plain")},
    )
    assert monthly_upload.status_code == 200
    assert monthly_upload.json()["attachments"][0]["original_filename"] == "lista-presenca.txt"

    attendance = client.post(
        f"/api/v1/polos/{polo['id']}/frequencias",
        headers=auth_headers,
        json={
            "beneficiario_id": beneficiario["id"],
            "modalidade_id": modalidade["id"],
            "activity_date": "2026-04-11",
            "present": True,
            "notes": "Presente no treino",
        },
    )
    assert attendance.status_code == 201
    attendance_body = attendance.json()
    assert attendance_body["beneficiario_id"] == beneficiario["id"]
    assert attendance_body["modalidade_id"] == modalidade["id"]
    assert attendance_body["present"] is True

    attendance_update = client.patch(
        f"/api/v1/polos/{polo['id']}/frequencias/{attendance_body['id']}",
        headers=auth_headers,
        json={"present": False, "notes": "Falta justificada"},
    )
    assert attendance_update.status_code == 200
    assert attendance_update.json()["present"] is False

    attendance_list = client.get(
        f"/api/v1/polos/{polo['id']}/frequencias",
        headers=auth_headers,
        params={"beneficiario_id": beneficiario["id"]},
    )
    assert attendance_list.status_code == 200
    assert [item["id"] for item in attendance_list.json()] == [attendance_body["id"]]

    occurrence = client.post(
        f"/api/v1/polos/{polo['id']}/ocorrencias",
        headers=auth_headers,
        json={
            "beneficiario_id": beneficiario["id"],
            "severity": "MEDIUM",
            "title": "Ocorrencia de teste",
            "description": "Registro operacional do polo",
        },
    )
    assert occurrence.status_code == 201
    occurrence_body = occurrence.json()
    assert occurrence_body["status"] == "OPEN"

    occurrence_update = client.patch(
        f"/api/v1/polos/{polo['id']}/ocorrencias/{occurrence_body['id']}",
        headers=auth_headers,
        json={"status": "CLOSED", "severity": "LOW"},
    )
    assert occurrence_update.status_code == 200
    assert occurrence_update.json()["status"] == "CLOSED"

    occurrence_list = client.get(
        f"/api/v1/polos/{polo['id']}/ocorrencias",
        headers=auth_headers,
        params={"status": "CLOSED"},
    )
    assert occurrence_list.status_code == 200
    assert [item["id"] for item in occurrence_list.json()] == [occurrence_body["id"]]

    audit_rows = db_session.execute(
        text(
            """
            select entity_schema, entity_name, action, count(*) as total
            from governance.audit_logs
            where entity_schema = 'polo'
              and entity_name in ('units', 'beneficiarios', 'modalidades', 'monthly_reports', 'frequencias', 'ocorrencias')
            group by entity_schema, entity_name, action
            """
        )
    ).all()

    assert {(row.entity_name, row.action): row.total for row in audit_rows} == {
        ("units", "CREATE"): 1,
        ("units", "UPDATE"): 1,
        ("beneficiarios", "CREATE"): 1,
        ("beneficiarios", "UPDATE"): 1,
        ("modalidades", "CREATE"): 1,
        ("modalidades", "UPDATE"): 1,
        ("monthly_reports", "CREATE"): 1,
        ("frequencias", "CREATE"): 1,
        ("frequencias", "UPDATE"): 1,
        ("ocorrencias", "CREATE"): 1,
        ("ocorrencias", "UPDATE"): 1,
    }
