"""
The views module defines the Flask views (web pages) for the application.
Each view is a function that returns an HTML template to render in the browser.
"""

from collections import OrderedDict
from pathlib import Path

import flask
import pandas as pd
import plotly.express as px

# Create a Flask Blueprint for the views
bp = flask.Blueprint("views", __name__)


@bp.route("/", methods=["GET"])
def index():
    """Serve the standard index page."""
    # Access the instance folder for application-specific data
    instance_path = Path(flask.current_app.instance_path)

    database_df = pd.read_csv(instance_path / "website_database.csv").reset_index()

    # Retrieve selected column to color by on the map. If no selection, default to "extracted_value".
    colour_by = flask.request.args.get("colour_by", default="measured_gwl")
    type_shown = flask.request.args.get("type_shown", default="cpt_and_bh")

    if type_shown == "only_cpt":
        database_df = database_df[database_df["type"] == "cpt"]
        marker_description_text = ""

    elif type_shown == "only_bh":
        database_df = database_df[database_df["type"] == "bh"]
        marker_description_text = ""

    else:
        marker_description_text = "Large markers show boreholes and small markers show CPTs"

    # Calculate the center of the map for visualization
    centre_lat = database_df["latitude"].mean()
    centre_lon = database_df["longitude"].mean()

    # Create an interactive scatter map using Plotly
    map = px.scatter_map(
        database_df,
        lat="latitude",  # Column specifying latitude
        lon="longitude",  # Column specifying longitude
        color=colour_by,  # Column specifying marker color
        hover_name=database_df["record_name"],
        zoom=5,
        size="type_as_number",  # Marker size
        center={"lat": centre_lat, "lon": centre_lon},  # Map center
        hover_data=OrderedDict(
            [  # Used to order the items in hover data (but lat and long are always first)
                ("measured_gwl", ":.2f"),
                ("model_gwl", ":.2f"),
                ("measured_minus_model", ":.2f"),
                ("type_as_number", False),
            ]
        )
    )

    # Render the map and data in an HTML template
    return flask.render_template(
        "views/index.html",
        map=map.to_html(
            full_html=False,  # Embed only the necessary map HTML
            include_plotlyjs=False,  # Exclude Plotly.js library (assume it's loaded separately)
            default_height="85vh",  # Set the map height
        ),
        colour_by=colour_by,
        type_shown=type_shown,
        colour_variables=[
            ("measured_gwl", "Measured ground water level"),
            ("model_gwl", "Ground water level from the National Water Table Model"),
            ("measured_minus_model", "Difference between measured and modelled ground water level"),
        ],
        type_shown_variables=[
            ("cpt_and_bh", "CPT and borehole"),
            ("only_cpt", "Only CPT"),
            ("only_bh", "Only borehole"),
        ],
        marker_description_text = marker_description_text,
    )