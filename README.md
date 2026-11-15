# MeterFlow

MeterFlow is a modular monolithic SaaS platform for API gateway metering, tenant-aware API key management, usage aggregation, subscriptions, billing, and analytics. It is designed as a production-minded Django foundation that can run locally as a single deployable service while keeping domain boundaries clean and ready for future extraction into dedicated services.

This repository is intended to serve as a working SaaS platform foundation for a gateway-focused product. It includes authentication, multi-tenancy, secure API key issuance, metering, quota enforcement, billing, analytics, Celery-based processing, and Docker-based deployment orchestration.

## Why this project exists

The core business problem is straightforward:

- API providers need to identify clients securely
- Tenants need isolation and ownership boundaries
- Requests need to be tracked and billed based on usage
- Gateway traffic needs protection and validation
- Billing and analytics need to be calculated on reliable aggregates
- The system should be deployable in a developer-friendly local setup while still reflecting production patterns

MeterFlow addresses these needs with a modular monolith architecture built in Django, backed by PostgreSQL, Redis, and Celery.

## Product capabilities

The current project includes:

- User registration and login with a custom Django user model
- Organization/tenant creation and membership-based access control
- Secure API key issuance, rotation, revocation, and verification
- Gateway request validation using API keys and allowlist-style upstream checks
- Request quota reservations and usage counter tracking
- Usage aggregation snapshots for Redis-backed counters
- Billing period generation and invoice creation flows
- Analytics summaries for usage, token totals, and endpoint activity
- Audit logging and operational metadata
- Celery Beat job scheduling for usage aggregation and billing runs
- Docker Compose orchestration for Postgres, Redis, Celery worker, Celery Beat, Nginx, Prometheus, and Grafana

## Architectural approach

MeterFlow uses a modular monolith instead of a microservice network at this stage because it gives a strong balance of:

- Clear separation of concerns by domain app
- Easy local development and testability
- Lower operational complexity during early product growth
- Natural boundaries for future service extraction if needed

The project is organized as multiple domain apps under the `apps/` directory, each with a dedicated responsibility:

- `apps.accounts` – authentication and user identity
- `apps.tenants` – organizations and membership roles
- `apps.api_keys` – API key lifecycle and verification
- `apps.gateway` – gateway request validation and request acceptance
- `apps.subscriptions` – plan and subscription models
- `apps.pricing` – pricing logic and rule management
- `apps.usage` – endpoint tracking, usage records, Redis counters, aggregation windows
- `apps.billing` – invoice generation and payment modeling
- `apps.analytics` – usage and tenant analytics summaries
- `apps.audit` – audit event and tracking support

## Tech stack

- Python 3.12+
- Django 4.2
- Django REST Framework
- PostgreSQL (production-oriented database target)
- Redis (usage counters, Celery broker/backend)
- Celery + Celery Beat
- Docker and Docker Compose
- SQLite fallback for local test execution in the dev environment
- pytest + pytest-django

## Repository structure

```text
masterflow/
├── apps/
│   ├── accounts/
│   ├── analytics/
│   ├── api_keys/
│   ├── audit/
│   ├── billing/
│   ├── gateway/
│   ├── pricing/
│   ├── subscriptions/
│   ├── tenants/
│   └── usage/
├── config/
│   ├── settings/
│   ├── celery.py
│   ├── urls.py
│   └── wsgi.py
├── docker/
├── docs/
├── requirements/
├── scripts/
├── tests/
├── .env.example
├── .gitignore
├── Dockerfile
├── Dockerfile.nginx
├── docker-compose.yml
├── manage.py
├── pyproject.toml
├── README.md
├── requirements.txt
└── test_db.sqlite3
```

## Core data model

The project models a SaaS platform that centers on an organization (tenant) and its users.

- `User` – custom identity model using email-based authentication
- `Organization` – tenant boundary for all usage/billing
- `Membership` – role assignment between user and organization
- `APIKey` – hashed credential used by clients for authenticated requests
- `APIEndpoint` – tracked API routes per tenant
- `UsageRecord` – billable or non-billable metering events
- `UsageAggregationWindow` – period bucket used for aggregated windowing
- `Invoice` and `InvoiceLineItem` – invoicing artifacts

## Security model

Security is a primary concern in this project.

- API keys are stored as salted PBKDF2 hashes instead of plain text
- Secret values are returned only once at creation time
- Requests are validated using allowed API key metadata and auth headers
- Gateway logic avoids trusting client-supplied tenant identifiers
- Upstream URL validation is designed to reduce SSRF-like risks in request forwarding logic
- Multi-tenancy boundaries keep tenant-owned usage and billing separate by organization

## Usage pipeline

The system is designed around a practical usage lifecycle:

1. A valid API key is used to authenticate a request
2. The gateway validates the request and records demand metadata
3. Usage counts are incremented in a Redis-friendly counter structure
4. A Celery task aggregates Redis counters into a durable database snapshot
5. The resultant usage records are available to billing and analytics services
6. Billing jobs generate invoice periods for active organizations

This gives the project a realistic at-least-once processing model with periodic reconciliation rather than assuming exactly-once behavior.

## Celery automation

Celery is configured to support asynchronous processing and scheduled jobs:

- `apps.usage.tasks.aggregate_usage_task` flushes Redis usage counters into the database
- `apps.billing.tasks.generate_monthly_invoices_task` prepares invoice windows for active tenants
- Beat is configured in `config/settings/base.py`

Configured schedules:

- usage aggregation every 5 minutes
- invoice generation daily (for the monthly billing flow)

## Docker and deployment

The project includes a Docker Compose setup with the key infrastructure components necessary for a local SaaS environment:

- PostgreSQL
- Redis
- Celery worker
- Celery Beat
- Nginx
- Prometheus
- Grafana

The stack includes restart policies and health checks to make it behave more like a hardened developer environment while still being lightweight enough for local development.

### Docker command examples

```bash
docker compose up --build

docker compose ps

docker compose logs -f celery-worker

docker compose logs -f celery-beat
```

### Health endpoint

The project exposes a basic health check endpoint:

```text
GET /healthz
```

This endpoint returns a simple JSON status payload for container and infrastructure health checks.

## Environment configuration

Copy the example environment file before running locally:

```powershell
Copy-Item .env.example .env
```

The environment file includes values for:

- Django configuration
- PostgreSQL connection details
- Redis and Celery configuration
- API key prefix
- logging level
- Grafana and Prometheus ports

Example values from `.env.example`:

```env
DJANGO_ENV=development
DJANGO_SECRET_KEY=change-me-in-production
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
DJANGO_CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
DATABASE_URL=sqlite:///./meterflow.sqlite3
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
API_KEY_PREFIX=mf_
LOG_LEVEL=INFO
```

## Getting started locally

### 1. Create a virtual environment

```powershell
cd C:\Users\nitty\PROGRAMS\masterflow
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements\dev.txt
```

### 3. Configure environment variables

```powershell
Copy-Item .env.example .env
```

### 4. Run migrations and start the app

```powershell
python manage.py migrate --settings=config.settings.test
python manage.py runserver 0.0.0.0:8000
```

The test settings default to SQLite when `METERFLOW_TEST_DATABASE=sqlite3`, which is convenient for local validation on Windows and CI-friendly environments.

## Running tests

```powershell
cd C:\Users\nitty\PROGRAMS\masterflow
.\.venv\Scripts\python.exe -m pytest -q
```

The project test suite currently validates the implemented SaaS foundation, including:

- auth and tenant creation
- API key lifecycle handling
- gateway acceptance flow
- invoice generation
- usage snapshot aggregation
- analytics summaries

## API overview

### Authentication endpoints

- `POST /api/v1/auth/register/` – register a new user
- `POST /api/v1/auth/login/` – login and receive authentication session/token behavior depending on the configuration

### Tenant endpoints

- `POST /api/v1/organizations/` – create a new organization
- `GET /api/v1/organizations/` – list accessible organizations

### API key endpoints

- `GET /api/v1/keys/` – list API keys
- `POST /api/v1/keys/` – create a new API key
- `DELETE /api/v1/keys/{id}/` – revoke or delete an API key
- `POST /api/v1/keys/{id}/rotate/` – rotate a key and reissue a new secret

### Gateway endpoints

- `POST /gateway/v1/request/` – submit a gateway request using a valid API key

### Billing and pricing

- `POST /api/v1/subscriptions/` – create or assign a subscription
- `GET /api/v1/pricing/` – fetch pricing rules
- `POST /api/v1/invoices/generate/` – generate an invoice on demand
- `GET /api/v1/invoices/` – list invoices

### Analytics

- `GET /api/v1/analytics/overview/` – organization usage overview

## Example request flow

A standard request path for a tenant could look like this:

1. Create an organization
2. Register a user and assign membership
3. Generate an API key for that organization
4. Submit a request to the gateway with the `Authorization: ApiKey <secret>` header
5. Usage is captured and sent to the aggregation pipeline
6. Celery aggregates counters into usage windows
7. Billing jobs generate invoices for the organization
8. Analytics queries aggregate and summarize the usage records

## Current project status

This repository is a working SaaS foundation for a modular monolithic API gateway platform. It is not a fully distributed microservice platform, and it does not attempt to simulate every advanced production system in one step. Instead, it focuses on building a solid domain-driven base that is practical, testable, and extensible.

The project is intentionally structured so it can evolve toward a fuller production architecture with:

- stronger RBAC policies
- more advanced rate limiting
- richer billing calculations
- deeper analytics dashboards
- stronger deployment environment segmentation
- operational monitoring and alerting

## Recommended next steps

If you want to continue the project beyond the current foundation, the most valuable next steps are:

- strengthen deduplication/idempotency in the aggregation pipeline
- add more granular billing rules from subscription plans and pricing rules
- expand analytics dashboards and time-series reporting
- add stronger RBAC and tenant-scoped authorization checks
- refine production Docker files and deployment scripts
- add integration tests covering Celery tasks and Redis flows

## Contributing

This project is designed for iterative product-building, so contributions should stay focused on domain boundaries and keep the modular structure explicit.

Best practices:

- keep app responsibilities narrow and clear
- prefer domain services over business logic in views
- maintain tests for critical flows
- ensure tenant boundaries are enforced in all services
- prefer secure and auditable operational behavior over shortcuts

## License

This repository is provided for educational and project-development purposes. Add your preferred license before production deployment if you intend to distribute or commercialize the application.
