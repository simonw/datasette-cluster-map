from datasette import hookimpl


@hookimpl
def extra_css_urls():
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
def extra_js_urls():
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
