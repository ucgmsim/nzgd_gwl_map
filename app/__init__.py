from pathlib import Path
from typing import Any

from flask import Flask


def create_app(test_config: Any = None):
    """Build a flask app for serving."""
    # create and configure the app
    app = Flask(
        __name__, instance_relative_config=True, static_url_path="/nzgd_gwl_map/static/"
    )

    # app_path = Path(app.instance_path)
    # static_path = Path(app.static_folder)
    # print("static_path:")
    # print(static_path)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # import our views and register them with the app.
    from app import views

    app.register_blueprint(views.bp)

    # ensure the instance folder exists
    app_path.mkdir(exist_ok=True)

    return app
