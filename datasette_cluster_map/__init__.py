from datasette import hookimpl


@hookimpl
def extra_css_urls():
    return [{
        "url": "https://unpkg.com/leaflet@1.0.3/dist/leaflet.css",
        "sri": "sha512-07I2e+7D8p6he1SIM+1twR5TIrhUQn9+I6yjqD53JQjFiMf8EtC93ty0/5vJTZGF8aAocvHYNEDJajGdNx1IsQ=="
    }, {
        "url": "https://unpkg.com/leaflet.markercluster@1.0.3/dist/MarkerCluster.css",
        "sri": "sha384-lPzjPsFQL6te2x+VxmV6q1DpRxpRk0tmnl2cpwAO5y04ESyc752tnEWPKDfl1olr"
    }, {
        "url": "https://unpkg.com/leaflet.markercluster@1.0.3/dist/MarkerCluster.Default.css",
        "sri": "sha384-5kMSQJ6S4Qj5i09mtMNrWpSi8iXw230pKU76xTmrpezGnNJQzj0NzXjQLLg+jE7k"
    }]


@hookimpl
def extra_js_urls():
	return [{
        "url": "https://unpkg.com/leaflet@1.0.3/dist/leaflet-src.js",
        "sri": "sha512-WXoSHqw/t26DszhdMhOXOkI7qCiv5QWXhH9R7CgvgZMHz1ImlkVQ3uNsiQKu5wwbbxtPzFXd1hK4tzno2VqhpA=="
    }, {
        "url": "https://unpkg.com/leaflet.markercluster@1.0.3/dist/leaflet.markercluster-src.js",
        "sri": "sha384-aPW7+bcmswg0D7N22za0Cj4RDQtJjUVz9obDfEeT0q8ekjOqn32IJt8Hmxqjl6jV"
    },
    "/-/static-plugins/datasette_cluster_map/datasette-cluster-map.js"]
