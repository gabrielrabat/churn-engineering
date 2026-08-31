# Pipeline Preditivo de Churn — FIAP PósTech (Tech Challenge Fase 1)

API REST para predição de propensão de churn de clientes de telecomunicações,
construída sobre um modelo `RandomForestClassifier` (Scikit-Learn) e servida
com FastAPI.

## Contexto

Uma operadora de telecomunicações está perdendo clientes em ritmo acelerado.
Este projeto cobre o pipeline completo: da análise exploratória dos dados até
o modelo servido via API, comparando modelos lineares, baseados em árvores e
redes neurais simples.

## Estrutura do projeto

```
churn_engineering/
├── src/                        # Código produtivo (fora dos notebooks)
│   ├── preprocessing.py        # Limpeza + one-hot encoding das features
│   ├── predict.py              # Inferência (predict_churn)
│   ├── model_loader.py         # Carrega models/champion_model.joblib
│   └── api/                    # API FastAPI
│       ├── main.py             # Bootstrap: app, middlewares, routers
│       ├── core.py             # Configurações (env vars)
│       ├── schemas.py          # Modelos Pydantic (request/response)
│       ├── auth.py             # Autenticação JWT
│       ├── logging_config.py   # Logs estruturados em JSON
│       ├── middleware.py       # Middleware de logging + trace_id
│       ├── metrics.py          # Métricas customizadas do Prometheus
│       ├── rate_limit.py       # Rate limiting (SlowAPI)
│       └── routers/
│           ├── auth.py         # POST /auth/login, GET /auth/me
│           ├── info.py         # GET /, /health, /model/info, /metrics
│           └── predict.py      # POST /predict, /predict/batch
├── data/                        # Dataset bruto (Telco_customer_churn.xlsx)
├── models/                      # Modelos treinados (.joblib) + comparação
├── notebooks/                   # EDA e comparação de modelos (experimentação)
├── docs/
│   └── model_card.md            # Performance, limitações e vieses do modelo
├── tests/                       # Testes automatizados (unitários + API, pytest)
├── Dockerfile                   # Imagem da API (produção)
├── requirements-api.txt         # Dependências mínimas para rodar a API
├── requirements.txt              # Dependências completas de desenvolvimento
├── docker-compose.yml            # Stack local: API + Prometheus
├── prometheus/                   # Configuração de scraping e alertas
├── render.yaml                   # Blueprint de deploy no Render (opcional)
└── .env.example                  # Variáveis de ambiente de referência
```

## Modelo

- **Algoritmo campeão:** `RandomForestClassifier`, escolhido por ter o maior
  F1 entre Regressão Logística, Random Forest e MLP (ver
  `notebooks/model_comparison.ipynb` e `models/model_comparison.csv`).
- **Artefato:** `models/champion_model.joblib` (Pipeline sklearn: pré-processamento + classificador).
- **Detalhes de performance, limitações e vieses:** ver [`docs/model_card.md`](docs/model_card.md).

## Rodando localmente (sem Docker)

Requer Python 3.12+.

```bash
python -m venv .venv
source .venv/Scripts/activate   # Windows (Git Bash) — no PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env
uvicorn src.api.main:app --reload
```

A API sobe em `http://localhost:8000`. Documentação interativa (Swagger) em
`http://localhost:8000/docs`.

## Rodando com Docker

```bash
docker compose up --build
```

- API: `http://localhost:8000/docs`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000`

## Usando a API

### 1. Autenticar

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=secret123"
```

Resposta: `{"access_token": "...", "token_type": "bearer"}`. Use o token nas
próximas chamadas: `Authorization: Bearer <access_token>`.

### 2. Predição individual

```bash
curl -X POST http://localhost:8000/predict \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "gender": "Female", "senior_citizen": "No", "partner": "Yes", "dependents": "No",
    "tenure_months": 1, "phone_service": "No", "multiple_lines": "No phone service",
    "internet_service": "DSL", "online_security": "No", "online_backup": "Yes",
    "device_protection": "No", "tech_support": "No", "streaming_tv": "No",
    "streaming_movies": "No", "contract": "Month-to-month", "paperless_billing": "Yes",
    "payment_method": "Electronic check", "monthly_charges": 29.85,
    "total_charges": 29.85, "cltv": 3239
  }'
```

### 3. Predição em lote

`POST /predict/batch` com `{"items": [ ... , ... ]}` (até `BATCH_MAX_ITEMS`,
padrão 100 clientes).

### Endpoints disponíveis

| Método | Rota | Auth | Descrição |
|---|---|---|---|
| GET | `/` | não | Info básica da API |
| GET | `/health` | não | Health check (usado pelo Docker/Render) |
| GET | `/model/info` | não | Metadados do modelo carregado |
| GET | `/metrics` | não | Métricas no formato Prometheus |
| POST | `/auth/login` | não | Autentica e retorna um JWT |
| GET | `/auth/me` | sim | Usuário associado ao token |
| POST | `/predict` | sim | Predição individual |
| POST | `/predict/batch` | sim | Predição em lote |

## Variáveis de ambiente

Ver [`.env.example`](.env.example) para a lista completa (JWT, rate limits,
CORS, credenciais de demonstração etc.).

## Testes

Testes automatizados com `pytest` já estão implementados (unitários e de API)
no diretório [`tests/`](tests/).

Para executar:

```bash
pytest -q
```

Estado atual da suíte: **77 testes passando**.

## Deploy (opcional)

Blueprint pronto em [`render.yaml`](render.yaml) para deploy no
[Render](https://render.com): sobe a API e uma instância de Prometheus
apontando para o endpoint público `/metrics`.
