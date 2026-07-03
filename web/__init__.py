"""Flask application factory for the Music Streaming Playlist Engine."""

import os

from flask import Flask


def create_app(config=None):
    """Create and configure the Flask application."""
    app = Flask(__name__,
                template_folder="templates",
                static_folder="static")
    app.config["SECRET_KEY"] = "music-engine-dev"
    if config:
        app.config.update(config)

    # Import and register routes
    from web.routes import register_routes
    register_routes(app)

    return app
