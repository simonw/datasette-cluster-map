import datasette
from datasette_test import wait_until_responds
import pytest
import sqlite3
from subprocess import Popen, PIPE
import sys


def pytest_report_header():
    return "Datasette: {}".format(datasette.__version__)


@pytest.fixture(scope="session")
def ds_server(tmp_path_factory):
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
            db.execute(
                f"""
                create table {latitude}_{longitude} (
                    id integer primary key,
                    {latitude} float,
                    {longitude} float
                )
            """
            )
            db.execute(
                f"""
                insert into {latitude}_{longitude} ({latitude}, {longitude})
                values (37.0167, -122.0024), (37.3184, -121.9511)
            """
            )
    process = Popen(
        [
            sys.executable,
            "-m",
            "datasette",
            "--port",
            "8126",
            str(db_path),
        ],
        stdout=PIPE,
    )
    wait_until_responds("http://localhost:8126/")
    yield "http://localhost:8126"
    process.terminate()
    process.wait()
