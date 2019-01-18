from datasette import hookimpl


@hookimpl
def extra_css_urls():
    return [
        {
            "url": "https://unpkg.com/leaflet@1.3.1/dist/leaflet.css",
            "sri": "sha512-Rksm5RenBEKSKFjgI3a41vrjkw4EVPlJ3+OiI65vTjIdo9brlAacEuKOiQ5OFh7cOI1bkDwLqdLw3Zg0cRJAAQ==",
        },
        {
            "url": "https://unpkg.com/leaflet.markercluster@1.3.0/dist/MarkerCluster.css",
            "sri": "sha384-lPzjPsFQL6te2x+VxmV6q1DpRxpRk0tmnl2cpwAO5y04ESyc752tnEWPKDfl1olr",
        },
        {
            "url": "https://unpkg.com/leaflet.markercluster@1.3.0/dist/MarkerCluster.Default.css",
            "sri": "sha384-5kMSQJ6S4Qj5i09mtMNrWpSi8iXw230pKU76xTmrpezGnNJQzj0NzXjQLLg+jE7k",
        },
    ]


@hookimpl
def extra_js_urls():
    return [
        {
            "url": "https://unpkg.com/leaflet@1.3.1/dist/leaflet.js",
            "sri": "sha512-/Nsx9X4HebavoBvEBuyp3I7od5tA0UzAxs+j83KgC8PU0kgB4XiK4Lfe4y4cgBtaRJQEIFCW+oC506aPT2L1zw==",
        },
        {
            "url": "https://unpkg.com/leaflet.markercluster@1.3.0/dist/leaflet.markercluster-src.js",
            "sri": "sha384-NAOEbWFcjnXc7U9GkULPhupHZNAbqru9dS3c+4ANYAwtFoVAWuVuMVDH0DIy4ESp",
        },
        "/-/static-plugins/datasette_cluster_map/datasette-cluster-map.js",
    ]


@hookimpl
def extra_body_script(template, database, table, datasette):
    config = (
        datasette.plugin_config("datasette-cluster-map", database=database, table=table)
        or {}
    )
    js = []
    for key in ("latitude", "longitude"):
        column_name = config.get("{}_column".format(key))
        if column_name:
            js.append(
                "window.DATASETTE_CLUSTER_MAP_{}_COLUMN = '{}';".format(
                    key.upper(), column_name
                )
            )
    return "\n".join(js)
