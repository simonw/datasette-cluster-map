import datasette
from datasette_test import wait_until_responds
import json
import pytest
import sqlite3
from subprocess import Popen, PIPE
import sys


def pytest_report_header():
    return "Datasette: {}".format(datasette.__version__)


@pytest.fixture(scope="session")
def ds_db_path(tmp_path_factory):
    tmpdir = tmp_path_factory.mktemp("tmp")
    db_path = str(tmpdir / "data.db")
    db = sqlite3.connect(db_path)
    for latitude, longitude in (
        ("latitude", "longitude"),
        ("lat", "lon"),
        ("lat", "lng"),
        ("lat", "long"),
        ("foo_latitude", "foo_longitude"),
    ):
        with db:
            db.execute(f"""
                create table {latitude}_{longitude} (
                    id integer primary key,
                    {latitude} float,
                    {longitude} float
                )
            """)
            db.execute(f"""
                insert into {latitude}_{longitude} ({latitude}, {longitude})
                values (37.0167, -122.0024), (37.3184, -121.9511)
            """)
    # 25 rows, more than the max_returned_rows of 10 set below
    with db:
        db.execute(
            "create table paginated (id integer primary key, latitude float, longitude float)"
        )
        db.executemany(
            "insert into paginated (latitude, longitude) values (?, ?)",
            [(37.0 + i * 0.01, -122.0 - i * 0.01) for i in range(25)],
        )
    db.close()
    return db_path


def _serve(db_path, port, *extra_args):
    process = Popen(
        [
            sys.executable,
            "-m",
            "datasette",
            "--port",
            str(port),
            "--setting",
            "max_returned_rows",
            "10",
            *extra_args,
            str(db_path),
        ],
        stdout=PIPE,
    )
    url = "http://localhost:{}".format(port)
    try:
        wait_until_responds(url + "/")
        yield url
    finally:
        process.terminate()
        process.wait()


@pytest.fixture(scope="session")
def ds_server(ds_db_path):
    yield from _serve(ds_db_path, 8126)


@pytest.fixture(scope="session")
def ds_server_no_referrer_policy(ds_db_path, tmp_path_factory):
    metadata_path = tmp_path_factory.mktemp("metadata") / "metadata.json"
    metadata_path.write_text(
        json.dumps(
            {
                "plugins": {
                    "datasette-cluster-map": {
                        "tile_layer_options": {"referrerPolicy": False}
                    }
                }
            }
        )
    )
    yield from _serve(ds_db_path, 8127, "--metadata", str(metadata_path))
