import pytest

try:
    from playwright import sync_api
except ImportError:
    sync_api = None
import pytest
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
