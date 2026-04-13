from sqlalchemy import text


def _create_demand(client, auth_headers):
    response = client.post(
        "/api/v1/demands",
        headers=auth_headers,
        json={
            "category": "SAUDE",
            "title": "Demanda para tarefa",
            "description": "Atendimento precisa de retorno",
            "priority": "MEDIUM",
        },
    )
    assert response.status_code == 201
    return response.json()


def test_list_tasks_requires_auth(client):
    response = client.get("/api/v1/tasks")
    assert response.status_code in (401, 403)


def test_create_task_persists_and_audits(client, auth_headers, db_session):
    response = client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={"task_type": "FOLLOW_UP", "title": "Tarefa de teste"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["task_type"] == "FOLLOW_UP"
    assert body["title"] == "Tarefa de teste"
    assert body["status"] == "OPEN"

    task_count = db_session.execute(text("select count(*) from workflow.tasks")).scalar_one()
    audit_count = db_session.execute(
        text(
            """
            select count(*)
            from governance.audit_logs
            where entity_schema = 'workflow'
              and entity_name = 'tasks'
              and action = 'CREATE'
            """
        )
    ).scalar_one()

    assert task_count == 1
    assert audit_count == 1


def test_task_lifecycle_resolves_linked_demand(client, auth_headers, admin_user, db_session):
    demand = _create_demand(client, auth_headers)

    create_task = client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={
            "demand_id": demand["id"],
            "assigned_to_user_id": str(admin_user.id),
            "task_type": "FIELD_VISIT",
            "title": "Visita operacional",
            "priority": "MEDIUM",
        },
    )
    assert create_task.status_code == 201
    task = create_task.json()
    assert task["demand_id"] == demand["id"]
    assert task["status"] == "OPEN"

    listed = client.get("/api/v1/tasks", headers=auth_headers, params={"demand_id": demand["id"]})
    assert listed.status_code == 200
    assert [item["id"] for item in listed.json()] == [task["id"]]

    update = client.patch(
        f"/api/v1/tasks/{task['id']}",
        headers=auth_headers,
        json={
            "status": "IN_PROGRESS",
            "priority": "HIGH",
        },
    )
    assert update.status_code == 200
    assert update.json()["status"] == "IN_PROGRESS"
    assert update.json()["priority"] == "HIGH"

    complete = client.post(
        f"/api/v1/tasks/{task['id']}/complete",
        headers=auth_headers,
        json={"resolution_notes": "Atendimento finalizado"},
    )
    assert complete.status_code == 200
    completed = complete.json()
    assert completed["status"] == "COMPLETED"
    assert completed["completed_at"] is not None

    refreshed_demand = client.get(f"/api/v1/demands/{demand['id']}", headers=auth_headers)
    assert refreshed_demand.status_code == 200
    assert refreshed_demand.json()["status"] == "RESOLVED"
    assert refreshed_demand.json()["resolution_notes"] == "Atendimento finalizado"

    audit_rows = db_session.execute(
        text(
            """
            select entity_schema, entity_name, action, count(*) as total
            from governance.audit_logs
            where (entity_schema, entity_name, action) in (
                ('territory', 'demands', 'CREATE'),
                ('territory', 'demands', 'RESOLVE'),
                ('workflow', 'tasks', 'CREATE'),
                ('workflow', 'tasks', 'UPDATE'),
                ('workflow', 'tasks', 'COMPLETE')
            )
            group by entity_schema, entity_name, action
            """
        )
    ).all()

    assert {(row.entity_schema, row.entity_name, row.action): row.total for row in audit_rows} == {
        ("territory", "demands", "CREATE"): 1,
        ("territory", "demands", "RESOLVE"): 1,
        ("workflow", "tasks", "CREATE"): 1,
        ("workflow", "tasks", "UPDATE"): 1,
        ("workflow", "tasks", "COMPLETE"): 1,
    }
