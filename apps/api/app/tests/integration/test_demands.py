from sqlalchemy import text


def _create_demand(client, auth_headers, payload=None):
    response = client.post(
        "/api/v1/demands",
        headers=auth_headers,
        json=payload
        or {
            "category": "SAUDE",
            "title": "Acompanhamento inicial",
            "description": "Checar necessidade do atendimento",
            "priority": "MEDIUM",
        },
    )
    assert response.status_code == 201
    return response.json()


def test_demand_lifecycle_assigns_and_creates_operational_task(client, auth_headers, admin_user, db_session):
    demand = _create_demand(client, auth_headers)

    detail = client.get(f"/api/v1/demands/{demand['id']}", headers=auth_headers)
    assert detail.status_code == 200
    assert detail.json()["title"] == "Acompanhamento inicial"

    update = client.patch(
        f"/api/v1/demands/{demand['id']}",
        headers=auth_headers,
        json={"priority": "HIGH", "description": "Priorizar retorno"},
    )
    assert update.status_code == 200
    assert update.json()["priority"] == "HIGH"
    assert update.json()["description"] == "Priorizar retorno"

    assign = client.post(
        f"/api/v1/demands/{demand['id']}/assign",
        headers=auth_headers,
        json={"assigned_to_user_id": str(admin_user.id)},
    )
    assert assign.status_code == 200
    assert assign.json()["assigned_to_user_id"] == str(admin_user.id)
    assert assign.json()["status"] == "ASSIGNED"

    task = client.post(
        f"/api/v1/demands/{demand['id']}/tasks",
        headers=auth_headers,
        json={
            "task_type": "FIELD_VISIT",
            "title": "Visita de acompanhamento",
        },
    )
    assert task.status_code == 201
    task_body = task.json()
    assert task_body["demand_id"] == demand["id"]
    assert task_body["assigned_to_user_id"] == str(admin_user.id)
    assert task_body["task_type"] == "FIELD_VISIT"
    assert task_body["priority"] == "HIGH"

    refreshed = client.get(f"/api/v1/demands/{demand['id']}", headers=auth_headers)
    assert refreshed.status_code == 200
    assert refreshed.json()["status"] == "IN_PROGRESS"

    audit_rows = db_session.execute(
        text(
            """
            select entity_schema, entity_name, action, count(*) as total
            from governance.audit_logs
            where (entity_schema, entity_name, action) in (
                ('territory', 'demands', 'CREATE'),
                ('territory', 'demands', 'UPDATE'),
                ('territory', 'demands', 'ASSIGN'),
                ('workflow', 'tasks', 'CREATE')
            )
            group by entity_schema, entity_name, action
            """
        )
    ).all()

    assert {(row.entity_schema, row.entity_name, row.action): row.total for row in audit_rows} == {
        ("territory", "demands", "CREATE"): 1,
        ("territory", "demands", "UPDATE"): 2,
        ("territory", "demands", "ASSIGN"): 1,
        ("workflow", "tasks", "CREATE"): 1,
    }
