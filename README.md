# datasette-cluster-map

[![PyPI](https://img.shields.io/pypi/v/datasette-cluster-map.svg)](https://pypi.python.org/pypi/datasette-cluster-map)
[![CircleCI](https://circleci.com/gh/simonw/datasette-cluster-map.svg?style=svg)](https://circleci.com/gh/simonw/datasette-cluster-map)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/simonw/datasette-cluster-map/blob/master/LICENSE)


A [Datasette plugin](http://datasette.readthedocs.io/en/latest/plugins.html) that detects tables with `latitude` and `longitude` columns and then plots them on a map using [Leaflet.markercluster](https://github.com/Leaflet/Leaflet.markercluster).

More about this project: [Datasette plugins, and building a clustered map visualization](https://simonwillison.net/2018/Apr/20/datasette-plugins/)

## Demo

[global-power-plants.datasettes.com](https://global-power-plants.datasettes.com/global-power-plants/global-power-plants) hosts a demo of this plugin running against a database of 33,000 power plants around the world.

![Cluster map demo](https://static.simonwillison.net/static/2020/global-power-plants.png)

## Installation

Run `pip install datasette-cluster-map` to add this plugin to your Datasette virtual environment. Datasette will automatically load the plugin if it is installed in this way.

If you are deploying using the `datasette publish` command you can use the `--install` option:

    datasette publish cloudrun mydb.db --install=datasette-cluster-map

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

You can also use a custom SQL query to rename those columns to `latitude` and `longitude`, [for example](https://polar-bears.now.sh/polar-bears?sql=select+*%2C%0D%0A++++%22Capture+Latitude%22+as+latitude%2C%0D%0A++++%22Capture+Longitude%22+as+longitude%0D%0Afrom+%5BUSGS_WC_eartag_deployments_2009-2011%5D):

    select *,
        "Capture Latitude" as latitude,
        "Capture Longitude" as longitude
    from [USGS_WC_eartag_deployments_2009-2011]

## How I deployed the demo

    datasette publish cloudrun global-power-plants.db \
        --service global-power-plants \
        --metadata metadata.json \
        --install=datasette-cluster-map \
        --extra-options="--config facet_time_limit_ms:1000"
