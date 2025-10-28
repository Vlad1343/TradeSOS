# Project Architecture & Recommended Structure

This document describes the current layout of the repository and a recommended package structure for clearer organization and easier testing.

Current important top-level files:
- `app.py` - application factory and Flask initialization
- `main.py` - local development entry point (runs `app.run()`)
- `routes.py` - all HTTP route handlers
- `models.py` - SQLAlchemy models
- `forms.py` - WTForms definitions
- `utils.py` - helper utilities (postcode parsing, notifications, etc.)
- `config.py` - configuration classes
- `templates/` - Jinja templates
- `static/` - CSS, JS, images

Recommended project structure (refactor plan)

- `src/tradesos/` - application package (move Python modules here)
  - `__init__.py` (creates the Flask app with factory pattern)
  - `config.py` (apps config)
  - `models.py`
  - `routes/` (subpackage with multiple route modules)
  - `forms.py`
  - `utils.py`
  - `services/` (business logic separated from route handlers)
- `templates/`
- `static/`
- `tests/` - unit and integration tests
- `docker/` - Docker manifests and Dockerfile (optional)
- `docs/` - architecture, deployment notes, and file descriptions

Why this helps
- Separates concerns and allows importing modules as a package (src layout).
- Easier to write tests and use CI tools.
- Clearer naming and grouping of related route handlers.

Migration tips
1. Create `src/tradesos` and add `__init__.py` that imports create_app and config.
2. Move files one-by-one and update imports (use relative imports inside package).
3. Run tests and start app locally to verify behavior before deleting old top-level files.

If you want, I can carry out the refactor by creating the `src/tradesos` package and moving or duplicating files with updated imports. I will not delete originals unless you confirm.
