from setuptools import setup
import os

VERSION = "0.18a0"


def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="datasette-cluster-map",
    description="Datasette plugin that shows a map for any data with latitude/longitude columns",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Simon Willison",
    url="https://github.com/simonw/datasette-cluster-map",
    project_urls={
        "Issues": "https://github.com/simonw/datasette-cluster-map/issues",
        "CI": "https://github.com/simonw/datasette-cluster-map/actions",
        "Changelog": "https://github.com/simonw/datasette-cluster-map/releases",
    },
    license="Apache License, Version 2.0",
    classifiers=[
        "Framework :: Datasette",
        "License :: OSI Approved :: Apache Software License",
    ],
    version=VERSION,
    packages=["datasette_cluster_map"],
    entry_points={"datasette": ["cluster_map = datasette_cluster_map"]},
    package_data={
        "datasette_cluster_map": [
            "static/*.js",
            "static/*.css",
        ]
    },
    install_requires=["datasette>=0.54", "datasette-leaflet>=0.2.2"],
    extras_require={"test": ["pytest", "pytest-asyncio", "httpx", "sqlite-utils"]},
)
