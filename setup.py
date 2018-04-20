from setuptools import setup
import os

VERSION = '0.2'


def get_long_description():
    with open(os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'README.md'
    ), encoding='utf8') as fp:
        return fp.read()


setup(
    name='datasette-cluster-map',
    description='Datasette plugin that shows a cluster map for any data with latitude/longitude columns',
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
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
