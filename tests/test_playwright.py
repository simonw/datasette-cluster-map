import base64
import nest_asyncio
from playwright import sync_api
import pytest

nest_asyncio.apply()


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


PNG_1X1 = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
)


def _tile_referers(page, url):
    "Load url with tile requests stubbed out, return their Referer headers"
    referers = []

    def handle(route):
        referers.append(route.request.all_headers().get("referer"))
        route.fulfill(status=200, content_type="image/png", body=PNG_1X1)

    page.route("https://tile.openstreetmap.org/**", handle)
    page.goto(url)
    sync_api.expect(page.locator(".leaflet-marker-icon")).to_have_count(2)
    sync_api.expect(page.locator("img.leaflet-tile-loaded").first).to_be_visible()
    assert referers
    return referers


def test_tiles_send_origin_as_referer(ds_server, page):
    # Datasette sends Referrer-Policy: no-referrer, but tile.openstreetmap.org
    # blocks requests that do not have a Referer
    response = page.request.get(ds_server + "/data/latitude_longitude")
    assert response.headers["referrer-policy"] == "no-referrer"
    referers = _tile_referers(page, ds_server + "/data/latitude_longitude")
    # Just the origin, not the path to the table
    assert set(referers) == {ds_server + "/"}


def test_tile_referrer_policy_can_be_disabled(ds_server_no_referrer_policy, page):
    referers = _tile_referers(
        page, ds_server_no_referrer_policy + "/data/latitude_longitude"
    )
    assert set(referers) == {None}
