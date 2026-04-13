def test_administration_foundation_links_funding_contract_and_budget(client, auth_headers):
    demo = client.post("/api/v1/demo/bootstrap", headers=auth_headers)
    assert demo.status_code == 200
    demo_body = demo.json()

    partner = client.post(
        "/api/v1/relationships/partners",
        headers=auth_headers,
        json={
            "organization_id": demo_body["organization"]["id"],
            "name": "Empresa Local Parceira",
            "partner_type": "EMPRESA",
            "contact_name": "Contato Empresa",
            "contact_phone": "31988880000",
            "district": "Vila Cristina",
            "contribution_area": "PATROCINIO",
            "service_offered": "Apoio para evento",
            "partnership_type": "PATROCINIO",
            "status": "ACTIVE",
        },
    )
    assert partner.status_code == 201

    field_event = client.post(
        "/api/v1/relationships/field-events",
        headers=auth_headers,
        json={
            "organization_id": demo_body["organization"]["id"],
            "polo_id": demo_body["polo"]["id"],
            "partner_id": partner.json()["id"],
            "title": "Evento de entrada - Vila Cristina",
            "district": "Vila Cristina",
            "event_type": "ACAO_SOCIAL",
            "event_date": "2026-04-11",
            "expected_people": 120,
        },
    )
    assert field_event.status_code == 201

    funding = client.post(
        "/api/v1/administration/funding-sources",
        headers=auth_headers,
        json={
            "organization_id": demo_body["organization"]["id"],
            "vereador_id": demo_body["vereador"]["id"],
            "source_type": "EMENDA_PARLAMENTAR",
            "name": "Emenda estrutura base 2026",
            "appropriation_number": "2026-0001",
            "estimated_amount": "50000.00",
            "secured_amount": "30000.00",
            "deposited_amount": "30000.00",
            "deposited_on": "2026-04-01",
            "status": "ACTIVE",
            "starts_on": "2026-01-01",
            "ends_on": "2026-12-31",
            "notes": "Fonte inicial para expansao controlada",
        },
    )
    assert funding.status_code == 201
    assert funding.json()["source_type"] == "EMENDA_PARLAMENTAR"

    contract = client.post(
        "/api/v1/administration/contracts",
        headers=auth_headers,
        json={
            "organization_id": demo_body["organization"]["id"],
            "partner_id": partner.json()["id"],
            "funding_source_id": funding.json()["id"],
            "contract_type": "TERMO_PARCEIRA",
            "title": "Termo de parceria evento Vila Cristina",
            "party_name": "Empresa Local Parceira",
            "amount": "5000.00",
            "status": "DRAFT",
            "starts_on": "2026-04-01",
            "ends_on": "2026-04-30",
            "document_ref": "contrato-parceria-001.pdf",
        },
    )
    assert contract.status_code == 201
    assert contract.json()["partner_id"] == partner.json()["id"]

    budget = client.post(
        "/api/v1/administration/budget-items",
        headers=auth_headers,
        json={
            "organization_id": demo_body["organization"]["id"],
            "funding_source_id": funding.json()["id"],
            "contract_id": contract.json()["id"],
            "polo_id": demo_body["polo"]["id"],
            "field_event_id": field_event.json()["id"],
            "category": "EVENTO_ACAO_SOCIAL",
            "description": "Material e logistica do evento de entrada",
            "planned_amount": "2500.00",
            "committed_amount": "1000.00",
            "paid_amount": "0.00",
            "status": "PLANNED",
            "due_on": "2026-04-11",
        },
    )
    assert budget.status_code == 201
    assert budget.json()["category"] == "EVENTO_ACAO_SOCIAL"
    assert budget.json()["field_event_id"] == field_event.json()["id"]

    deposit = client.post(
        "/api/v1/administration/financial-movements",
        headers=auth_headers,
        json={
            "funding_source_id": funding.json()["id"],
            "polo_id": demo_body["polo"]["id"],
            "movement_type": "PREFEITURA_DEPOSITO",
            "description": "Deposito da Prefeitura na conta da REVISA",
            "amount": "30000.00",
            "movement_date": "2026-04-01",
            "document_ref": "extrato-deposito-001.pdf",
        },
    )
    assert deposit.status_code == 201
    assert deposit.json()["vereador_id"] == demo_body["vereador"]["id"]

    payment = client.post(
        "/api/v1/administration/financial-movements",
        headers=auth_headers,
        json={
            "funding_source_id": funding.json()["id"],
            "polo_id": demo_body["polo"]["id"],
            "budget_item_id": budget.json()["id"],
            "contract_id": contract.json()["id"],
            "movement_type": "COMPRA_PAGAMENTO",
            "description": "Pagamento de compra de materiais",
            "amount": "1000.00",
            "movement_date": "2026-04-10",
            "document_ref": "nota-fiscal-001.pdf",
        },
    )
    assert payment.status_code == 201

    purchase = client.post(
        "/api/v1/administration/purchase-requests",
        headers=auth_headers,
        json={
            "organization_id": demo_body["organization"]["id"],
            "polo_id": demo_body["polo"]["id"],
            "funding_source_id": funding.json()["id"],
            "requester_name": "Administrador Polo 31",
            "category": "BENS_PERMANENTES",
            "description": "Compra de materiais para o polo",
            "approved_amount": "1000.00",
            "status": "REQUESTED",
            "needed_on": "2026-04-15",
            "document_ref": "cotacao-materiais-001.pdf",
            "items": [
                {
                    "product": "Colchonete de ginastica",
                    "size": "90-100cm",
                    "desired_brand": "Kikos",
                    "quantity": "30",
                    "unit": "un",
                    "estimated_unit_price": "40.00",
                    "notes": "2-3 cm de espessura. Cor preta ou azul",
                }
            ],
        },
    )
    assert purchase.status_code == 201
    assert purchase.json()["vereador_id"] == demo_body["vereador"]["id"]
    assert purchase.json()["estimated_amount"] == "1200.00"
    assert purchase.json()["requester_name"] == "Administrador Polo 31"
    assert purchase.json()["items"][0]["product"] == "Colchonete de ginastica"
    assert purchase.json()["items"][0]["line_number"] == 1

    asset = client.post(
        "/api/v1/administration/permanent-assets",
        headers=auth_headers,
        json={
            "organization_id": demo_body["organization"]["id"],
            "polo_id": demo_body["polo"]["id"],
            "funding_source_id": funding.json()["id"],
            "purchase_request_id": purchase.json()["id"],
            "purchase_request_item_id": purchase.json()["items"][0]["id"],
            "asset_type": "BEM_PERMANENTE",
            "description": "Colchonete de ginastica",
            "brand": "Kikos",
            "acquisition_date": "2026-04-16",
            "acquisition_value": "1200.00",
            "location_label": "Polo Teste",
        },
    )
    assert asset.status_code == 201
    assert asset.json()["asset_number"].startswith("REVISA-PAT-")
    assert asset.json()["label_text"].startswith(asset.json()["asset_number"])

    assets = client.get(
        "/api/v1/administration/permanent-assets",
        headers=auth_headers,
        params={"polo_id": demo_body["polo"]["id"]},
    )
    assert assets.status_code == 200
    assert [item["id"] for item in assets.json()] == [asset.json()["id"]]

    purchase_alerts = client.get("/api/v1/administration/purchase-alerts", headers=auth_headers)
    assert purchase_alerts.status_code == 200
    assert purchase_alerts.json()["open_purchase_requests"] >= 1
    assert purchase.json()["id"] in [item["id"] for item in purchase_alerts.json()["purchase_requests"]]

    staff_person = client.post(
        "/api/v1/persons",
        headers=auth_headers,
        json={"full_name": "Colaborador Polo Demo", "phone": "11977770000"},
    )
    assert staff_person.status_code == 201

    staff = client.post(
        "/api/v1/administration/staff-contracts",
        headers=auth_headers,
        json={
            "organization_id": demo_body["organization"]["id"],
            "polo_id": demo_body["polo"]["id"],
            "funding_source_id": funding.json()["id"],
            "person_id": staff_person.json()["id"],
            "role_title": "Instrutor de apoio",
            "contract_type": "TEMPORARIO",
            "salary_amount": "2500.00",
            "starts_on": "2026-04-01",
            "ends_on": "2026-12-31",
        },
    )
    assert staff.status_code == 201
    assert staff.json()["status"] == "ACTIVE"

    budgets = client.get(
        "/api/v1/administration/budget-items",
        headers=auth_headers,
        params={"category": "EVENTO_ACAO_SOCIAL"},
    )
    assert budgets.status_code == 200
    assert [item["id"] for item in budgets.json()] == [budget.json()["id"]]

    movements = client.get(
        "/api/v1/administration/financial-movements",
        headers=auth_headers,
        params={"funding_source_id": funding.json()["id"]},
    )
    assert movements.status_code == 200
    assert {item["id"] for item in movements.json()} == {deposit.json()["id"], payment.json()["id"]}

    report = client.get(
        "/api/v1/administration/accountability-report",
        headers=auth_headers,
        params={
            "funding_source_id": funding.json()["id"],
            "polo_id": demo_body["polo"]["id"],
        },
    )
    assert report.status_code == 200
    report_body = report.json()
    assert report_body["vereador_id"] == demo_body["vereador"]["id"]
    assert report_body["totals"]["deposited_amount"] == "30000.00"
    assert report_body["totals"]["movement_inflows"] == "30000.00"
    assert report_body["totals"]["movement_outflows"] == "1000.00"
    assert report_body["totals"]["available_balance"] == "29000.00"
    assert [item["id"] for item in report_body["purchase_requests"]] == [purchase.json()["id"]]
    assert [item["id"] for item in report_body["staff_contracts"]] == [staff.json()["id"]]
    assert {item["document_ref"] for item in report_body["fiscal_documents"]} == {
        "contrato-parceria-001.pdf",
        "extrato-deposito-001.pdf",
        "nota-fiscal-001.pdf",
        "cotacao-materiais-001.pdf",
    }

    export = client.get(
        "/api/v1/administration/accountability-report/export",
        headers=auth_headers,
        params={"funding_source_id": funding.json()["id"]},
    )
    assert export.status_code == 200
    assert "text/csv" in export.headers["content-type"]
    assert "PREFEITURA_DEPOSITO" in export.text
    assert "nota-fiscal-001.pdf" in export.text
    assert "captacao" in export.text

    parliamentary_without_vereador = client.post(
        "/api/v1/administration/funding-sources",
        headers=auth_headers,
        json={
            "organization_id": demo_body["organization"]["id"],
            "source_type": "EMENDA_IMPOSITIVA",
            "name": "Emenda sem vereador",
        },
    )
    assert parliamentary_without_vereador.status_code == 422

    institutional_funding = client.post(
        "/api/v1/administration/funding-sources",
        headers=auth_headers,
        json={
            "organization_id": demo_body["organization"]["id"],
            "source_type": "DOACAO",
            "name": "Doacao empresa socialmente responsavel",
            "estimated_amount": "20000.00",
            "secured_amount": "20000.00",
            "deposited_amount": "20000.00",
            "deposited_on": "2026-05-01",
            "status": "ACTIVE",
        },
    )
    assert institutional_funding.status_code == 201
    assert institutional_funding.json()["vereador_id"] is None

    institutional_budget = client.post(
        "/api/v1/administration/budget-items",
        headers=auth_headers,
        json={
            "organization_id": demo_body["organization"]["id"],
            "funding_source_id": institutional_funding.json()["id"],
            "category": "DESPESAS_OPERACIONAIS",
            "description": "Locacao de espaco para projeto aprovado",
            "planned_amount": "5000.00",
            "committed_amount": "5000.00",
            "paid_amount": "0.00",
            "status": "PLANNED",
        },
    )
    assert institutional_budget.status_code == 201

    institutional_deposit = client.post(
        "/api/v1/administration/financial-movements",
        headers=auth_headers,
        json={
            "funding_source_id": institutional_funding.json()["id"],
            "movement_type": "ENTRADA",
            "description": "Entrada de doacao na conta da REVISA",
            "amount": "20000.00",
            "movement_date": "2026-05-01",
        },
    )
    assert institutional_deposit.status_code == 201
    assert institutional_deposit.json()["vereador_id"] is None
    assert institutional_deposit.json()["polo_id"] is None

    institutional_purchase = client.post(
        "/api/v1/administration/purchase-requests",
        headers=auth_headers,
        json={
            "organization_id": demo_body["organization"]["id"],
            "funding_source_id": institutional_funding.json()["id"],
            "category": "INSUMOS",
            "description": "Compra institucional sem polo",
            "status": "REQUESTED",
            "items": [
                {
                    "product": "Material de oficina",
                    "quantity": "1",
                    "unit": "lote",
                    "estimated_unit_price": "1000.00",
                }
            ],
        },
    )
    assert institutional_purchase.status_code == 201
    assert institutional_purchase.json()["vereador_id"] is None
    assert institutional_purchase.json()["polo_id"] is None

    institutional_asset = client.post(
        "/api/v1/administration/permanent-assets",
        headers=auth_headers,
        json={
            "organization_id": demo_body["organization"]["id"],
            "funding_source_id": institutional_funding.json()["id"],
            "purchase_request_id": institutional_purchase.json()["id"],
            "purchase_request_item_id": institutional_purchase.json()["items"][0]["id"],
            "asset_type": "BEM_PERMANENTE",
            "description": "Notebook projeto institucional",
            "location_label": "Sede REVISA",
        },
    )
    assert institutional_asset.status_code == 201
    assert institutional_asset.json()["vereador_id"] is None

    institutional_report = client.get(
        "/api/v1/administration/accountability-report",
        headers=auth_headers,
        params={"funding_source_id": institutional_funding.json()["id"]},
    )
    assert institutional_report.status_code == 200
    institutional_report_body = institutional_report.json()
    assert institutional_report_body["vereador_id"] is None
    assert institutional_report_body["totals"]["deposited_amount"] == "20000.00"
    assert institutional_report_body["totals"]["movement_inflows"] == "20000.00"
    assert [item["id"] for item in institutional_report_body["budget_items"]] == [institutional_budget.json()["id"]]
    assert [item["id"] for item in institutional_report_body["purchase_requests"]] == [institutional_purchase.json()["id"]]
