from datasette_cluster_map import extra_css_urls, extra_js_urls
from datasette.app import Datasette
import pytest
import sqlite_utils
import httpx


@pytest.fixture(scope="session")
def db_path(tmp_path_factory):
    db_directory = tmp_path_factory.mktemp("dbs")
    db_path = db_directory / "test.db"
    db = sqlite_utils.Database(db_path)
    db["places"].insert_all(
        [
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
        ],
        pk="id",
    )
    return db_path


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "config,expected_fragments",
    [
        (
            {},
            [
                'window.DATASETTE_CLUSTER_MAP_TILE_LAYER = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"'
            ],
        ),
        (
            {
                "tile_layer": "https://stamen-tiles-{s}.a.ssl.fastly.net/watercolor/{z}/{x}/{y}.{ext}"
            },
            [
                'window.DATASETTE_CLUSTER_MAP_TILE_LAYER = "https://stamen-tiles-{s}.a.ssl.fastly.net/watercolor/{z}/{x}/{y}.{ext}"'
            ],
        ),
        (
            {
                "tile_layer": "https://stamen-tiles-{s}.a.ssl.fastly.net/watercolor/{z}/{x}/{y}.{ext}",
                "tile_layer_options": {"minZoom": 1, "maxZoom": 16},
            },
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
            [
                'window.DATASETTE_CLUSTER_MAP_LATITUDE_COLUMN = "lat";',
                'window.DATASETTE_CLUSTER_MAP_LONGITUDE_COLUMN = "lng";',
                'window.DATASETTE_CLUSTER_MAP_CONTAINER = "#map-goes-here";',
            ],
        ),
    ],
)
async def test_plugin_config(db_path, config, expected_fragments):
    app = Datasette(
        [db_path], metadata={"plugins": {"datasette-cluster-map": config}}
    ).app()
    async with httpx.AsyncClient(app=app) as client:
        response = await client.get("http://localhost/test/places")
        assert response.status_code == 200
        for fragment in expected_fragments:
            assert fragment in response.text


@pytest.mark.asyncio
async def test_plugin_is_installed():
    app = Datasette([], memory=True).app()
    async with httpx.AsyncClient(app=app) as client:
        response = await client.get("http://localhost/-/plugins.json")
        assert response.status_code == 200
        installed_plugins = {p["name"] for p in response.json()}
        assert "datasette-cluster-map" in installed_plugins
        # Check JavaScript is correctly served
        response = await client.get(
            "http://localhost/-/static-plugins/datasette_cluster_map/datasette-cluster-map.js"
        )
        assert response.status_code == 200
        assert "const clusterMapEscapeHTML" in response.text


def test_extra_css_urls():
    assert isinstance(extra_css_urls(), list)


def test_extra_js_urls():
    assert isinstance(extra_js_urls(), list)
