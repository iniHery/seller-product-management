---
applyTo: "backend/**/*.py"
---

# Backend Instructions

## Framework

- Python
- Django
- Django REST Framework
- PostgreSQL
- Django ORM

## Architecture

Keep responsibilities separated:

- models
- serializers
- views
- urls
- permissions
- services when needed

Do not move unrelated logic between layers.

## API

- Reuse existing API structure.
- Preserve existing response format.
- Do not create duplicate endpoints.
- Do not change existing endpoint contracts without explaining why.

## Authentication

- Use Django REST Framework TokenAuthentication.
- Do not use JWT unless explicitly requested.
- Authentication header:

  Authorization: Token <token>

## Authorization

- Seller data must be scoped to the authenticated seller.
- Product access must be restricted to the owning seller.
- Backend authorization is authoritative.
- Never rely only on frontend authorization.

## Validation

- Backend validation is required.
- Reuse Django model validators and DRF serializer validation where appropriate.
- Do not duplicate validation unnecessarily.

## Database

- PostgreSQL is the development database.
- Use Django ORM.
- Preserve UUID primary keys where already implemented.
- Do not change schema without explicit requirement.

## Changes

- Make minimal changes.
- Do not change authentication or database architecture without justification.
- Do not invent major architectural patterns.
- Do not modify frontend files for backend-only tasks unless integration requires it.

## Validation

After backend changes:

```bash
python manage.py check