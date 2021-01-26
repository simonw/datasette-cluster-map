from datasette import hookimpl
import json


TILE_LAYER = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
TILE_LAYER_OPTIONS = {
    "maxZoom": 19,
    "detectRetina": True,
    "attribution": '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
}


@hookimpl
def extra_js_urls(database, table, columns, view_name, datasette):
    if not has_columns(database, table, columns, view_name, datasette):
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
    if not has_columns(database, table, columns, view_name, datasette):
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
    for key in ("latitude_column", "longitude_column", "container"):
        value = config.get(key)
        if value:
            js.append(
                "window.DATASETTE_CLUSTER_MAP_{} = {};".format(
                    key.upper(), json.dumps(value)
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


def has_columns(database, table, columns, view_name, datasette):
    if view_name not in ("database", "table"):
        return False
    if not columns:
        return False
    columns = [column.lower() for column in columns]
    config = (
        datasette.plugin_config("datasette-cluster-map", database=database, table=table)
        or {}
    )
    latitude_column = config.get("latitude_column") or "latitude"
    longitude_column = config.get("longitude_column") or "longitude"
    return latitude_column.lower() in columns and longitude_column.lower() in columns
