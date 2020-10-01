from datasette import hookimpl
import json


TILE_LAYER = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
TILE_LAYER_OPTIONS = {
    "maxZoom": 19,
    "detectRetina": True,
    "attribution": '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
}


@hookimpl
def extra_css_urls(database, table, columns, view_name, datasette):
    if not has_columns(database, table, columns, view_name, datasette):
        return []
    return [
        {
            "url": "https://unpkg.com/leaflet@1.5.1/dist/leaflet.css",
            "sri": "sha512-xwE/Az9zrjBIphAcBb3F6JVqxf46+CDLwfLMHloNu6KEQCAWi6HcDUbeOfBIptF7tcCzusKFjFw2yuvEpDL9wQ==",
        },
        {
            "url": "https://unpkg.com/leaflet.markercluster@1.4.1/dist/MarkerCluster.css",
            "sri": "sha384-lPzjPsFQL6te2x+VxmV6q1DpRxpRk0tmnl2cpwAO5y04ESyc752tnEWPKDfl1olr",
        },
        {
            "url": "https://unpkg.com/leaflet.markercluster@1.4.1/dist/MarkerCluster.Default.css",
            "sri": "sha384-5kMSQJ6S4Qj5i09mtMNrWpSi8iXw230pKU76xTmrpezGnNJQzj0NzXjQLLg+jE7k",
        },
    ]


@hookimpl
def extra_js_urls(database, table, columns, view_name, datasette):
    if not has_columns(database, table, columns, view_name, datasette):
        return []
    return [
        {
            "url": "https://unpkg.com/leaflet@1.5.1/dist/leaflet.js",
            "sri": "sha512-GffPMF3RvMeYyc1LWMHtK8EbPv0iNZ8/oTtHPx9/cc2ILxQ+u905qIwdpULaqDkyBKgOaB57QTMg7ztg8Jm2Og==",
        },
        {
            "url": "https://unpkg.com/leaflet.markercluster@1.4.1/dist/leaflet.markercluster-src.js",
            "sri": "sha384-N9K+COcUk7tr9O2uHZVp6jl7ueGhWsT+LUKUhd/VpA0svQrQMGArhY8r/u/Pkwih",
        },
        "/-/static-plugins/datasette_cluster_map/datasette-cluster-map.js",
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
