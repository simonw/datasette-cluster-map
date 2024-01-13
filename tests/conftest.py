import datasette


def pytest_report_header():
    return "Datasette: {}".format(datasette.__version__)
