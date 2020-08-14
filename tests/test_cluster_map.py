from datasette_cluster_map import extra_css_urls, extra_js_urls
from datasette.app import Datasette
import pytest
import httpx


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
