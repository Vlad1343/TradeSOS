"""main package initializer for TradeSOS application.

This file makes the `main` directory a Python package so imports like
`from main.models import ...` work reliably when running the app as
`FLASK_APP=main.app`.
"""

__all__ = ["app", "models", "routes"]
