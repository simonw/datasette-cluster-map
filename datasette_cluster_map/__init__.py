from datasette import hookimpl
from typing import List
import json


TILE_LAYER = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
TILE_LAYER_OPTIONS = {
    "maxZoom": 19,
    "attribution": '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
}


@hookimpl
def extra_js_urls(database, table, columns, view_name, datasette):
    if not find_columns(database, table, columns, view_name, datasette):
        return []
    return [
        {
            "url": datasette.urls.static_plugins(
                "datasette-cluster-map", "datasette-cluster-map.js"
            ),
            "module": True,
        }
    ]


@hookimpl
def extra_body_script(database, table, columns, view_name, datasette):
    location_columns = find_columns(database, table, columns, view_name, datasette)
    if not location_columns:
        return []
    config = (
        datasette.plugin_config("datasette-cluster-map", database=database, table=table)
        or {}
    )
    js = []
    js.append(
        "window.DATASETTE_CLUSTER_MAP_TILE_LAYER = {};".format(
            json.dumps(config.get("tile_layer") or TILE_LAYER)
        )
    )
    js.append(
        "window.DATASETTE_CLUSTER_MAP_TILE_LAYER_OPTIONS = {};".format(
            json.dumps(config.get("tile_layer_options") or TILE_LAYER_OPTIONS)
        )
    )

    # Add cluster_map_options if present
    if "cluster_map_options" in config:
        js.append(
            f"window.DATASETTE_CLUSTER_MAP_OPTIONS = {json.dumps(config['cluster_map_options'])};"
        )
    if config.get("container"):
        js.append(
            "window.DATASETTE_CLUSTER_MAP_CONTAINER = {};".format(
                json.dumps(config["container"])
            )
        )
    # latitude_column and longitude_column
    js.append(
        "window.DATASETTE_CLUSTER_MAP_LATITUDE_COLUMN = {};".format(
            json.dumps(location_columns[0])
        )
    )
    js.append(
        "window.DATASETTE_CLUSTER_MAP_LONGITUDE_COLUMN = {};".format(
            json.dumps(location_columns[1])
        )
    )
    js.append("window.datasette = window.datasette || {};")
    js.append(
        "datasette.cluster_map = {\n"
        + "    MARKERCLUSTER_URL: '{}',\n".format(
            datasette.urls.static_plugins(
                "datasette-cluster-map", "leaflet.markercluster.min.js"
            )
        )
        + "    MARKERCLUSTER_CSS_URL: '{}'\n}};".format(
            datasette.urls.static_plugins(
                "datasette-cluster-map", "leaflet.markercluster.css"
            )
        )
    )
    return "\n".join(js)


def find_columns(database, table, columns, view_name, datasette):
    if view_name not in ("database", "table"):
        return []
    if not columns:
        return []
    # If columns are configured, check for those
    columns = [column.lower() for column in columns]

    config = (
        datasette.plugin_config("datasette-cluster-map", database=database, table=table)
        or {}
    )
    latitude_column = config.get("latitude_column")
    longitude_column = config.get("longitude_column")

    if not latitude_column or not longitude_column:
        # Detect those columns instead
        location_columns = location_columns_from_columns(columns)
        if not location_columns:
            return []
        latitude_column, longitude_column = location_columns

    if latitude_column.lower() in columns and longitude_column.lower() in columns:
        return [latitude_column, longitude_column]


def _match(pattern, column):
    # latitude matches "latitude" or "foo_latitude"
    return column.lower() == pattern or column.lower().endswith("_" + pattern)


LATITUDE_PATTERNS = ["latitude", "lat"]
LONGITUDE_PATTERNS = ["longitude", "lon", "lng", "long"]
LOCATION_PRIORITIES = (
    ("latitude", "longitude"),
    ("lat", "lon"),
    ("lat", "lng"),
    ("lat", "long"),
)


def location_columns_from_columns(columns: List[str]) -> List[str]:
    latitude_col = None
    longitude_col = None
    lowercase_columns = [col.lower() for col in columns]
    cols_to_case = {col.lower(): col for col in columns}

    # First look for the priority pairings - return if found
    for lat, lon in LOCATION_PRIORITIES:
        if lat in lowercase_columns and lon in lowercase_columns:
            return [cols_to_case[lat], cols_to_case[lon]]

    # Now try for the wildcard patterns instead
    for col in columns:
        if any(_match(lat, col) for lat in LATITUDE_PATTERNS):
            if latitude_col is not None:
                # Already have latitude, so this is ambiguous
                return []
            latitude_col = col
        elif any(_match(lon, col) for lon in LONGITUDE_PATTERNS):
            if longitude_col is not None:
                # Already have longitude, so this is ambiguous
                return []
            longitude_col = col

    if latitude_col is None or longitude_col is None:
        return []

    return [latitude_col, longitude_col]
