# Seller Product Management - Copilot Instructions

## Project

This is an internship mini-project called:

"Sistem Manajemen Produk Seller"

The project follows requirements provided by the internship mentor.

The main goal is to understand and implement a Full Stack Web Application using Vue 3 as frontend and Django REST Framework as backend.

This is also a learning project. Generated code must remain understandable to the developer.

---

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
- Tailwind CSS v4
- Vue Router
- Axios
- Pinia

---

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

---

## Backend Rules

- Use Django REST Framework.
- Use Serializer.
- Use APIView where appropriate.
- Keep models, serializers, views, URLs, and permissions separated by responsibility.
- Backend must perform validation.
- Backend must enforce authorization.
- Use Django ORM for database access.
- Use PostgreSQL.
- Use UUID as primary key according to the project requirement.

---

## Frontend Rules

- Use Vue 3.
- Use Vue Router.
- Use Pinia for appropriate shared state, especially authentication state.
- Use Axios.
- Reuse the existing Axios instance.
- Reuse existing API service modules.
- Use Tailwind CSS v4.
- Keep Vue components focused on clear responsibilities.
- Do not put the entire application logic into one component.

---

## Authentication Rules

- Authentication uses Django REST Framework TokenAuthentication.
- Do not use JWT unless explicitly requested.
- Authorization header format:

  Authorization: Token <token>

- Never hardcode authentication tokens.
- Never hardcode passwords or credentials.
- Use the existing authentication store and Axios interceptor.

---

## Coding Rules

- Use clear variable and function names.
- Avoid unnecessary duplicate code.
- Do not add unnecessary dependencies.
- Do not change the architecture without explaining why.
- Do not implement features outside the current task unless required.
- Keep implementation aligned with the mentor's requirements.
- Prefer minimal changes.
- Preserve existing functionality.
- Do not perform large refactors for small tasks.

---

## UI and Responsive Rules

- Use Tailwind CSS v4.
- Keep visual design consistent across pages.
- Support mobile, tablet, and desktop.
- Avoid unnecessary fixed widths.
- Avoid horizontal overflow at page level.
- Tables may use local horizontal scrolling when necessary.
- Keep text readable on all backgrounds.
- Use responsive Tailwind utilities such as:
  - sm
  - md
  - lg
  - xl

---

## API Rules

- Reuse existing API endpoints.
- Do not create new endpoints unless explicitly required.
- Do not create duplicate Axios instances.
- Keep API logic inside service modules where appropriate.
- Preserve the existing API response structure.

---

## Agent / Copilot Behavior

Before implementing a complex task:

1. Inspect the current codebase.
2. Identify relevant files.
3. Create a short implementation plan.
4. Identify ambiguous or unspecified requirements.
5. Do not invent major architectural decisions.
6. Keep changes limited to the current task.

When implementing:

1. Reuse existing code where appropriate.
2. Avoid modifying unrelated files.
3. Preserve current functionality.
4. Do not modify backend for frontend-only tasks.
5. Do not modify frontend for backend-only tasks unless integration requires it.

After implementation:

1. Run appropriate checks or tests.
2. Run `npm run build` after frontend changes.
3. Run `python manage.py check` after backend changes.
4. Report files changed.
5. Explain what was implemented.
6. Explain how it works.
7. Explain how frontend and backend communicate.
8. Report unresolved issues.

---

## Learning Rule

For important implementation decisions, explain:

- What was implemented
- Why it was implemented
- How it works
- Which file is responsible
- How frontend and backend communicate

The developer should be able to understand the generated code instead of merely accepting it.

---

## Safety and Project Integrity

Never:

- Hardcode tokens
- Hardcode passwords
- Commit `.env`
- Modify the database schema without an explicit requirement
- Remove existing features without explanation
- Replace existing authentication with another mechanism
- Add a dependency when the existing stack is sufficient
- Invent API endpoints without justification