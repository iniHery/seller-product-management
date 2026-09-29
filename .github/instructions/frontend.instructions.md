---
applyTo: "frontend/src/**/*.vue,frontend/src/**/*.js,frontend/src/**/*.css"
---

# Frontend Instructions

## Framework

- Vue 3
- Vite
- Tailwind CSS v4
- Vue Router
- Pinia
- Axios

## Vue

- Use `<script setup>`.
- Prefer `ref`, `reactive`, and `computed` appropriately.
- Keep components focused.
- Use props and emits for parent-child communication.
- Reuse existing components where appropriate.
- Avoid putting unrelated business logic into a single component.

## API

- Use the existing Axios instance.
- Use existing API service modules.
- Do not create duplicate Axios instances.
- Do not hardcode API credentials.
- Do not hardcode authentication tokens.

## Authentication

- Authentication uses Django REST Framework TokenAuthentication.
- Use:
  `Authorization: Token <token>`
- Do not change to JWT unless explicitly requested.
- Reuse the existing Pinia auth store.

## Routing

- Reuse the existing Vue Router configuration.
- Preserve protected routes.
- Do not create duplicate route guards.

## Styling

- Use Tailwind CSS v4.
- Prefer utility classes over custom CSS.
- Keep spacing and typography consistent.
- Support mobile, tablet, and desktop.
- Avoid unnecessary fixed widths.
- Avoid page-level horizontal overflow.
- Tables may use local horizontal scrolling.

## UI

- Preserve existing functionality.
- Loading, empty, error, success, and confirmation states should remain usable.
- Text must remain readable against its background.
- Keep buttons consistent across pages.

## Changes

- Make the smallest reasonable change.
- Do not modify unrelated files.
- Do not refactor large sections unless requested.
- Do not add dependencies unless necessary and explicitly approved.

## Validation

After frontend changes:

```bash
npm run build