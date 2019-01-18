# datasette-cluster-map

[![PyPI](https://img.shields.io/pypi/v/datasette-cluster-map.svg)](https://pypi.python.org/pypi/datasette-cluster-map)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/simonw/datasette-cluster-map/blob/master/LICENSE)


A [Datasette plugin](http://datasette.readthedocs.io/en/latest/plugins.html) that detects tables with `latitude` and `longitude` columns and then plots them on a map using [Leaflet.markercluster](https://github.com/Leaflet/Leaflet.markercluster).

More about this project: [Datasette plugins, and building a clustered map visualization](https://simonwillison.net/2018/Apr/20/datasette-plugins/)

## Demo

[datasette-cluster-map-demo.datasettes.com](https://datasette-cluster-map-demo.datasettes.com/) hosts a demo of this plugin running against several different tables.

![Cluster map demo](https://static.simonwillison.net/static/2018/datasette-cluster-map.png)

## Installation

Run `pip install datasette-cluster-map` to add this plugin to your Datasette virtual environment. Datasette will automatically load the plugin if it is installed in this way.

If you are deploying using the `datasette publish` command you can use the `--install` option:

    datasette publish now mydb.db --install=datasette-cluster-map

If any of your tables have a `latitude` and `longitude` column, a map will be automatically displayed.

If your columns are called something else you can configure the column names using [plugin configuration](https://datasette.readthedocs.io/en/stable/plugins.html#plugin-configuration) in a `metadata.json` file. For example, if all of your columns are called `xlat` and `xlng` you can create a `metadata.json` file like this:

    {
        "title": "Regular metadata keys can go here too",
        "plugins": {
            "datasette-cluster-map": {
                "latitude_column": "xlat",
                "longitude_column": "xlng"
            }
        }
    }

Then run Datasette like this:

    datasette mydata.db -m metadata.json

This will configure the required column names for every database loaded by that Datasette instance.

If you want to customize the column names for just one table in one database, you can do something like this:

    {
        "databases": {
            "polar-bears": {
                "tables": {
                    "USGS_WC_eartag_deployments_2009-2011": {
                        "plugins": {
                            "datasette-cluster-map": {
                                "latitude_column": "Capture Latitude",
                                "longitude_column": "Capture Longitude"
                            }
                        }
                    }
                }
            }
        }
    }

You can also use a custom SQL query to rename those columns to `latitude` and `longitude`, [for example](https://datasette-cluster-map-demo.datasettes.com/polar-bears-455fe3a?sql=select+*%2C+%22Capture+Latitude%22+as+latitude%2C+%22Capture+Longitude%22+as+longitude+from+[USGS_WC_eartag_deployments_2009-2011]):

    select *,
      "Capture Latitude" as latitude,
      "Capture Longitude" as longitude
    from [USGS_WC_eartag_deployments_2009-2011]

## How I deployed the demo

    datasette publish now \
        --install=datasette-cluster-map \
        --name="datasette-cluster-map-demo" \
        --alias="datasette-cluster-map-demo.datasettes.com" \
        polar-bears.db sf-trees.db
