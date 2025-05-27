import pytest

try:
    from playwright import sync_api
except ImportError:
    sync_api = None
import nest_asyncio

nest_asyncio.apply()

pytestmark = pytest.mark.skipif(sync_api is None, reason="playwright not installed")


@pytest.mark.parametrize(
    "table",
    (
        "foo_latitude_foo_longitude",
        "lat_lng",
        "lat_lon",
        "lat_long",
        "latitude_longitude",
    ),
)
def test_markers_are_displayed(ds_server, table, page):
    page.goto(ds_server + "/data/" + table)
    # There should be two leaflet-marker-icons
    sync_api.expect(page.locator(".leaflet-marker-icon")).to_have_count(2)


def test_map_instance_stored(ds_server, page):
    page.goto(ds_server + "/data/lat_lng")
    # Wait for the map container to appear
    container = page.wait_for_selector(".leaflet-container")
    # Confirm that the datasetteClusterMap property exists on the leaflet map element
    has_trait = container.evaluate("el => 'datasetteClusterMap' in el")
    assert has_trait, "Element does not have datasetteClusterMap property"
