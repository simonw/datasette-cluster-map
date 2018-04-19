from setuptools import setup

VERSION = '0.1'

setup(
    name='datasette-cluster-map',
    description='Datasette plugin that shows a cluster map for any data with latitude/longitude columns',
    author='Simon Willison',
    url='https://github.com/simonw/datasette-cluster-map',
    license='Apache License, Version 2.0',
    version=VERSION,
    packages=['datasette_cluster_map'],
    entry_points={
        'datasette': [
            'cluster_map = datasette_cluster_map'
        ],
    },
    package_data={
        'datasette_cluster_map': [
            'static/datasette-cluster-map.js',
        ],
    },
    install_requires=['datasette']
)
