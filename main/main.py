# main.py - Application entrypoint used for local development.
# This file exposes a runnable entrypoint which starts the Flask development
# server. In production the app is served by a WSGI server (gunicorn).
from app import app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
