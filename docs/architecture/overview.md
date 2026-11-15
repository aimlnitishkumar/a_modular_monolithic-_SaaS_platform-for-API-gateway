# MeterFlow architecture overview

## Business context

MeterFlow is designed for multi-tenant API gateway and billing workloads. The platform must handle tenant isolation, request authentication, rate-limiting, usage metering, pricing, and invoice generation without writing a row per request to PostgreSQL.

## Architectural decision

We begin with a modular monolith for the first phase because it gives the team:

- clear app boundaries
- fewer distributed-system failure modes
- a simpler data model for multi-tenancy
- strong transaction boundaries around billing flows
- easy scaling to a future service-oriented design if demand justifies it

## System components

1. Django web/API layer
   - handles authentication and CRUD endpoints
   - orchestrates domain services
   - enforces permissions and tenant isolation

2. PostgreSQL
   - durable source of truth for tenant, plan, invoice, usage aggregation, audit, and payment data
   - supports relational integrity and transactional billing workflows

3. Redis
   - stores hot-path request counters
   - supports rate limiting and quota enforcement
   - powers short-lived usage state and queue coordination

4. Celery + Celery Beat
   - asynchronous usage aggregation
   - periodic billing and reconciliation tasks
   - retry-safe worker processing

5. Nginx
   - front-door proxy
   - central place for request buffering, TLS termination, and HTTP concerns

6. Observability stack
   - Prometheus scrapes service metrics
   - Grafana displays operational dashboards
   - structured logs provide traceability for security and billing events

## Why not microservices yet?

The business problem does not require service decomposition at MVP. A modular monolith keeps the design simpler and lowers operational risk while still enforcing clear boundaries. If later traffic or ownership changes justify specialization, each app can still be extracted with smaller blast radius.

## Multi-tenancy design

Tenant context should be resolved from the authenticated principal and permission layer. Under no circumstance should customer input directly determine the tenant record used for billing or quota logic.

## Failure model

The system is designed around at-least-once processing with idempotent persistence. Redis counters and Celery tasks can fail independently. Durable billing and usage aggregation rely on database constraints and idempotency keys rather than assumptions of exactly-once processing.

## Phase 1 concerns

This phase is intentionally limited to the foundation: architecture, app partitioning, environment structure, and deployment model. Domain logic will be introduced only once these foundations are stable.
