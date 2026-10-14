from flask import Flask


def create_app(config=None):
    app = Flask(__name__)
    app.config["TESTING"] = False
    if config:
        app.config.update(config)

    # In-memory store, fresh per app instance (so tests stay isolated)
    app.extensions["store"] = {
        "boreholes": {},
        "samples": {},
        "counters": {"borehole": 0, "sample": 0},
    }

    from app.routes import bp
    app.register_blueprint(bp)
    return app
