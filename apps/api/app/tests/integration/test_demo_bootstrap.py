from sqlalchemy import text


def test_demo_bootstrap_is_idempotent_and_returns_demo_graph(client, auth_headers, db_session):
    first = client.post("/api/v1/demo/bootstrap", headers=auth_headers)
    assert first.status_code == 200
    first_body = first.json()
    assert first_body["created"]
    assert first_body["organization"]["id"]
    assert first_body["polo"]["id"]
    assert first_body["person"]["id"]
    assert first_body["capture"]["status"] == "CONVERTED_TO_DEMAND"
    assert first_body["demand"]["status"] == "IN_PROGRESS"
    assert first_body["task"]["status"] == "OPEN"
    assert first_body["beneficiary"]["status"] == "ATIVO"

    second = client.post("/api/v1/demo/bootstrap", headers=auth_headers)
    assert second.status_code == 200
    second_body = second.json()
    assert second_body["created"] == []
    assert second_body["organization"]["id"] == first_body["organization"]["id"]
    assert second_body["polo"]["id"] == first_body["polo"]["id"]
    assert second_body["person"]["id"] == first_body["person"]["id"]
    assert second_body["capture"]["id"] == first_body["capture"]["id"]
    assert second_body["demand"]["id"] == first_body["demand"]["id"]
    assert second_body["task"]["id"] == first_body["task"]["id"]

    counts = db_session.execute(
        text(
            """
            select
              (select count(*) from core.organizations where document_number = 'REVISA-DEMO-POLO') as organizations,
              (select count(*) from core.persons where phone = '11900000001') as persons,
              (select count(*) from territory.contacts_capture where origin = 'WEB_DEMO' and phone = '11900000001') as captures,
              (select count(*) from territory.demands where title = 'Atendimento demo') as demands,
              (select count(*) from workflow.tasks where title = 'Retorno - Atendimento demo') as tasks,
              (select count(*) from polo.units where code = 'DEMO') as polos,
              (select count(*) from polo.beneficiarios) as beneficiaries,
              (select count(*) from polo.frequencias) as attendances,
              (select count(*) from polo.ocorrencias where title = 'Ocorrencia de demo') as occurrences
            """
        )
    ).one()

    assert counts.organizations == 1
    assert counts.persons == 1
    assert counts.captures == 1
    assert counts.demands == 1
    assert counts.tasks == 1
    assert counts.polos == 1
    assert counts.beneficiaries == 1
    assert counts.attendances == 1
    assert counts.occurrences == 1
