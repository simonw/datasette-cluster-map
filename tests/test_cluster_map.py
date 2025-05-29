from datasette_cluster_map import location_columns_from_columns
from datasette.app import Datasette
import pytest
import sqlite_utils
import textwrap


@pytest.fixture(scope="session")
def db_path(tmp_path_factory):
    db_directory = tmp_path_factory.mktemp("dbs")
    db_path = str(db_directory / "test.db")
    db = sqlite_utils.Database(db_path)
    places = [
        {
            "id": 1,
            "name": "The Mystery Spot",
            "address": "465 Mystery Spot Road, Santa Cruz, CA 95065",
            "latitude": 37.0167,
            "longitude": -122.0024,
        },
        {
            "id": 2,
            "name": "Winchester Mystery House",
            "address": "525 South Winchester Boulevard, San Jose, CA 95128",
            "latitude": 37.3184,
            "longitude": -121.9511,
        },
    ]
    db["places"].insert_all(
        places,
        pk="id",
    )
    db["places_caps"].insert_all(
        [
            {"id": p["id"], "LATITUDE": p["latitude"], "LONGITUDE": p["longitude"]}
            for p in places
        ],
        pk="id",
    )
    db.create_view(
        "places_lat_lng",
        "select id, name, address, latitude as lat, longitude as lng from places",
    )
    db["dogs"].insert({"id": 1, "name": "Cleq"}, pk="id")
    return db_path


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "config,table,expected_fragments",
    [
        (
            {},
            "places",
            [
                'window.DATASETTE_CLUSTER_MAP_TILE_LAYER = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"'
            ],
        ),
        (
            {
                "tile_layer": "https://stamen-tiles-{s}.a.ssl.fastly.net/watercolor/{z}/{x}/{y}.{ext}"
            },
            "places",
            [
                'window.DATASETTE_CLUSTER_MAP_TILE_LAYER = "https://stamen-tiles-{s}.a.ssl.fastly.net/watercolor/{z}/{x}/{y}.{ext}"'
            ],
        ),
        (
            {
                "tile_layer": "https://stamen-tiles-{s}.a.ssl.fastly.net/watercolor/{z}/{x}/{y}.{ext}",
                "tile_layer_options": {"minZoom": 1, "maxZoom": 16},
            },
            "places",
            [
                'window.DATASETTE_CLUSTER_MAP_TILE_LAYER = "https://stamen-tiles-{s}.a.ssl.fastly.net/watercolor/{z}/{x}/{y}.{ext}"',
                'window.DATASETTE_CLUSTER_MAP_TILE_LAYER_OPTIONS = {"minZoom": 1, "maxZoom": 16};',
            ],
        ),
        (
            {
                "latitude_column": "lat",
                "longitude_column": "lng",
                "container": "#map-goes-here",
            },
            "places_lat_lng",
            [
                'window.DATASETTE_CLUSTER_MAP_LATITUDE_COLUMN = "lat";',
                'window.DATASETTE_CLUSTER_MAP_LONGITUDE_COLUMN = "lng";',
                'window.DATASETTE_CLUSTER_MAP_CONTAINER = "#map-goes-here";',
            ],
        ),
        # This one should detect the columns even though they aren't configured
        (
            {},
            "places_lat_lng",
            [
                'window.DATASETTE_CLUSTER_MAP_LATITUDE_COLUMN = "lat";',
                'window.DATASETTE_CLUSTER_MAP_LONGITUDE_COLUMN = "lng";',
            ],
        ),
        # Test cluster_map_options emits correct JS
        (
            {"cluster_map_options": {"spiderfyOnMaxZoom": False}},
            "places",
            ['window.DATASETTE_CLUSTER_MAP_OPTIONS = {"spiderfyOnMaxZoom": false};'],
        ),
    ],
)
async def test_plugin_config(db_path, config, table, expected_fragments):
    ds = Datasette([db_path], metadata={"plugins": {"datasette-cluster-map": config}})
    response = await ds.client.get("/test/{}".format(table))
    assert response.status_code == 200
    for fragment in expected_fragments:
        assert fragment in response.text


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "path,should_have_javascript",
    [
        ("/", False),
        ("/test", False),
        ("/test?sql=select+1+-+1;", False),
        ("/test?sql=select+*+from+places;", True),
        ("/-/settings", False),
        ("/test/dogs", False),
        ("/test/places", True),
        ("/test/places_caps", True),
    ],
)
async def test_plugin_only_on_tables_or_queries_with_columns(
    db_path, path, should_have_javascript
):
    ds = Datasette([db_path])
    fragments = ("/datasette-cluster-map.js", "window.DATASETTE_CLUSTER_MAP_TILE_LAYER")
    response = await ds.client.get(path)
    assert response.status_code == 200
    if should_have_javascript:
        for fragment in fragments:
            assert fragment in response.text
    else:
        for fragment in fragments:
            assert fragment not in response.text


@pytest.mark.asyncio
async def test_plugin_is_installed():
    ds = Datasette([], memory=True)
    response = await ds.client.get("/-/plugins.json")
    assert response.status_code == 200
    installed_plugins = {p["name"] for p in response.json()}
    assert "datasette-cluster-map" in installed_plugins
    # Check JavaScript is correctly served
    response = await ds.client.get(
        "/-/static-plugins/datasette_cluster_map/datasette-cluster-map.js"
    )
    assert response.status_code == 200
    assert "const clusterMapEscapeHTML" in response.text


@pytest.mark.asyncio
async def test_respects_base_url():
    ds = Datasette([], memory=True, settings={"base_url": "/foo/"})
    response = await ds.client.get("/_memory?sql=select+1+as+latitude,+2+as+longitude")
    assert (
        textwrap.dedent(
            """
    datasette.cluster_map = {
        MARKERCLUSTER_URL: '/foo/-/static-plugins/datasette-cluster-map/leaflet.markercluster.min.js',
        MARKERCLUSTER_CSS_URL: '/foo/-/static-plugins/datasette-cluster-map/leaflet.markercluster.css'
    };"""
        ).strip()
        in response.text
    )


@pytest.mark.parametrize(
    "input,expected",
    (
        ([], []),
        (["a", "b"], []),
        (["a", "b", "latitude", "longitude"], ["latitude", "longitude"]),
        (["a", "b", "lat", "lon", "c"], ["lat", "lon"]),
        (["a", "b", "lat", "lng", "c"], ["lat", "lng"]),
        (["a", "b", "lat", "long", "c"], ["lat", "long"]),
        # Wildcard matches
        (["a", "foo_latitude", "foo_longitude"], ["foo_latitude", "foo_longitude"]),
        (["a", "foo_latitude", "bar_longitude"], ["foo_latitude", "bar_longitude"]),
        (["a", "foo_lat", "foo_long"], ["foo_lat", "foo_long"]),
        (["a", "foo_lat", "foo_lon"], ["foo_lat", "foo_lon"]),
        (["a", "foo_lat", "foo_lng"], ["foo_lat", "foo_lng"]),
        # latitude, longitude takes priority over country_long
        # https://github.com/simonw/datasette-cluster-map/issues/39#issuecomment-1890310833
        (["country_long", "latitude", "longitude"], ["latitude", "longitude"]),
        # latitude, longitude takes priority:
        (["a", "lat", "lon", "c", "latitude", "longitude"], ["latitude", "longitude"]),
        # Ambiguous wildcards:
        (["a", "foo_lat", "foo_lng", "foo_latitude", "foo_longitude"], []),
    ),
)
def test_location_columns_from_columns(input, expected):
    actual = location_columns_from_columns(input)
    actual_cap = location_columns_from_columns([col.upper() for col in input])
    assert actual == expected
    assert actual_cap == [col.upper() for col in expected]
