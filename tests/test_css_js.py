from datasette_cluster_map import extra_css_urls, extra_js_urls


def test_extra_css_urls():
    assert isinstance(extra_css_urls(), list)


def test_extra_js_urls():
    assert isinstance(extra_js_urls(), list)
