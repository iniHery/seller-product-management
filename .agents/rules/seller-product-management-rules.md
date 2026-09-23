---
trigger: always_on
---

# Seller Product Management Project Rules

## Project

This is an internship mini-project called:

"Sistem Manajemen Produk Seller"

The project follows requirements provided by the internship mentor.

The main goal is to understand and implement a Full Stack Web Application using Vue 3 as frontend and Django REST Framework as backend.

## Technology Stack

### Backend
- Python
- Django
- Django REST Framework
- PostgreSQL
- Django ORM

### Frontend
- Vue 3
- Vite
- Tailwind CSS
- Vue Router
- Axios
- Pinia

## Core Requirements

### Authentication
- Register
- Login
- Logout
- Get current authenticated user

### Authorization
- A seller can only access products belonging to that seller.
- A seller cannot modify or delete products belonging to another seller.
- Authorization must be enforced by the backend.

### Product
Product must support:
- List
- Create
- Detail
- Update
- Partial update
- Delete
- Search by name
- Search by SKU
- Filter by category
- Filter by status
- Pagination

Product fields:
- UUID primary key
- seller
- category
- name
- sku
- description
- price
- stock
- status
- created_at
- updated_at

### Category

Category must support:
- List
- Create
- Detail
- Update
- Partial update
- Delete

Category fields:
- UUID primary key
- name
- created_at
- updated_at

### Dashboard

Dashboard must display:
- Total products
- Active products
- Inactive products
- Total stock

### UX

The application should handle:
- Loading state
- Empty state
- Error state
- Success notification
- Delete confirmation

## Backend Rules

- Use Django REST Framework.
- Use Serializer.
- Understand and use APIView.
- Keep models, serializers, views, URLs, and permissions separated by responsibility.
- Backend must perform validation.
- Backend must enforce authorization.
- Use Django ORM for database access.
- Use PostgreSQL.
- Use UUID as primary key according to the project requirement.

## Frontend Rules

- Use Vue 3.
- Use Vue Router.
- Use Pinia for appropriate shared state, especially authentication state.
- Use Axios.
- Prefer a reusable Axios instance.
- Prefer reusable API service modules.
- Use Tailwind CSS.
- Keep Vue components focused on clear responsibilities.
- Do not put the entire application logic into one component.

## Coding Rules

- Use clear variable and function names.
- Avoid unnecessary duplicate code.
- Do not add unnecessary dependencies.
- Do not change the architecture without explaining why.
- Do not implement features outside the current task unless required.
- Keep implementation aligned with the mentor's requirements.

## Agent Rules

Before implementing a complex task:

1. Inspect the current codebase.
2. Identify relevant files.
3. Create an implementation plan.
4. Identify ambiguous or unspecified requirements.
5. Do not invent major architectural decisions.
6. Wait for review before major implementation when planning/review is available.

After implementation:

1. Run appropriate checks or tests.
2. Report files changed.
3. Explain what was implemented.
4. Explain how it was verified.
5. Report unresolved issues.

## Learning Rule

This is also a learning project.

For important implementation decisions, explain:
- what was implemented,
- why it was implemented,
- how it works,
- how frontend and backend communicate.

The generated code must remain understandable to the developer.