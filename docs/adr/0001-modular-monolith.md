# ADR-0001: Use a modular monolith as the initial architecture

- Status: Accepted
- Date: 2026-11-14

## Context

MeterFlow must support multi-tenancy, API key security, usage metering, quotas, billing, and analytics in a way that can scale from an early SaaS product into a larger platform. The initial product should be simple to reason about, operate, test, and evolve while retaining clear boundaries for future extraction.

## Decision

We will begin with a modular monolith implemented as a Django project with separate app packages for accounts, tenants, api_keys, gateway, subscriptions, pricing, usage, billing, analytics, and audit.

## Rationale

- Clear responsibilities keep the system easier to reason about.
- A single database and application runtime simplify transactional correctness around billing.
- Security policies and tenant isolation are easier to enforce consistently.
- The architecture remains suitable for future service extraction when internal requirements demand it.
- This approach reduces initial complexity compared with distributed services at MVP stage.

## Consequences

### Positive

- Faster startup and development velocity.
- Easier local reproducibility with Docker Compose.
- Simpler transaction and data consistency patterns around invoices and billing periods.
- Better fit for a product team that is still validating the business model.

### Negative

- Shared runtime can create coupling if app boundaries are not preserved.
- A large Django monolith may require discipline to prevent app-level sprawl.
- Scaling may eventually require decomposition.

## Follow-up

If traffic and operational load justify it, each app can be extracted as a service while preserving the business contracts and data model already established.
