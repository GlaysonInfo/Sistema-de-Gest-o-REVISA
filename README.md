# REVISA Platform

Backend FastAPI da plataforma REVISA.

## Requisitos

- Python 3.11+
- PostgreSQL 16

## Instalacao rapida

```bash
cp .env.example .env
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -e .
alembic upgrade head
python scripts/seed_initial_data.py
python scripts/bootstrap_admin.py
uvicorn app.main:app --reload
```

## Testes

```bash
cd apps/api
pytest -q
```

## Frontend de demo

```bash
python -m http.server 5173 -d apps/web
```

Acesse `http://127.0.0.1:5173` com a API rodando em `http://127.0.0.1:8000`.
Entre com `admin` / `Admin@123` e use o botao `Preparar demo` para criar os dados de apresentacao.

## Sistema Web Modulo Polo

```bash
python -m http.server 5174 -d apps/polo
```

Acesse `http://127.0.0.1:5174` com a API do modulo apontada no campo `API`.
Entre com `admin` / `Admin@123` e use `Preparar contexto` para operar como administrador de Polo.
Se a porta `8000` ja estiver ocupada por uma API antiga, rode a API atualizada em outra porta, como `http://127.0.0.1:8001`, e ajuste o campo `API` na tela.

## Aplicativo mobile de campo

```bash
python -m http.server 5175 -d apps/mobile
```

Acesse `http://127.0.0.1:5175` com a API rodando em `http://127.0.0.1:8000`.
Use `Preparar contexto` para preencher organizacao e polo de demo, depois envie cadastros de beneficiarios do polo ou pessoas para acompanhamento de mandato.

## Contratos

O contrato OpenAPI consolidado fica em `packages/domain-contracts/openapi/openapi.yaml`.
