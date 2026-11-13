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


def test_markers_are_displayed_for_sql_query(ds_server, page):
    # Datasette 1.0 rejects ?_extra=count for queries with a 400 error
    page.goto(ds_server + "/data?sql=select+*+from+latitude_longitude")
    sync_api.expect(page.locator(".leaflet-marker-icon")).to_have_count(2)


def test_load_all_paginates_through_table(ds_server, page):
    responses = []
    page.on(
        "response",
        lambda response: ".json" in response.url and responses.append(response),
    )
    page.goto(ds_server + "/data/paginated")
    progress = page.locator(".leaflet-container + div")
    sync_api.expect(progress).to_contain_text("Showing 10 of 25 (40%)")
    page.get_by_role("button", name="load all").click()
    # Progress message is cleared once every page has been fetched
    sync_api.expect(progress).to_be_empty()
    assert [response.status for response in responses] == [200, 200, 200]
