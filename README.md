<!-- These are examples of badges you might want to add to your README:
     please update the URLs accordingly

[![Built Status](https://api.cirrus-ci.com/github/<USER>/soda-data.svg?branch=main)](https://cirrus-ci.com/github/<USER>/soda-data)
[![ReadTheDocs](https://readthedocs.org/projects/soda-data/badge/?version=latest)](https://soda-data.readthedocs.io/en/stable/)
[![Coveralls](https://img.shields.io/coveralls/github/<USER>/soda-data/main.svg)](https://coveralls.io/r/<USER>/soda-data)
[![PyPI-Server](https://img.shields.io/pypi/v/soda-data.svg)](https://pypi.org/project/soda-data/)
[![Conda-Forge](https://img.shields.io/conda/vn/conda-forge/soda-data.svg)](https://anaconda.org/conda-forge/soda-data)
[![Monthly Downloads](https://pepy.tech/badge/soda-data/month)](https://pepy.tech/project/soda-data)
[![Twitter](https://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Twitter)](https://twitter.com/soda-data)
-->

<!-- [![Built Status](https://api.cirrus-ci.com/github/<USER>/soda-data.svg?branch=main)](https://cirrus-ci.com/github/<USER>/soda-data)
[![ReadTheDocs](https://readthedocs.org/projects/soda-data/badge/?version=latest)](https://soda-data.readthedocs.io/en/stable/)
[![Coveralls](https://img.shields.io/coveralls/github/<USER>/soda-data/main.svg)](https://coveralls.io/r/<USER>/soda-data) -->
<!-- [![PyPI-Server](https://img.shields.io/pypi/v/soda-data.svg)](https://pypi.org/project/soda-data/) -->
<!-- [![Conda-Forge](https://img.shields.io/conda/vn/conda-forge/soda-data.svg)](https://anaconda.org/conda-forge/soda-data) -->
<!-- [![Monthly Downloads](https://pepy.tech/badge/soda-data/month)](https://pepy.tech/project/soda-data) -->
<!-- [![Twitter](https://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Twitter)](https://twitter.com/soda-data) -->

# SourceData Dataset

> The Source Data dataset: a biological annotated dataset for machine learning and AI in the publishing context.

A longer description of your project goes here...

<!-- pyscaffold-notes -->

## Obtaining the data:

### From a Neo4j dump

If a neo4j instance is in place and with a SourceData dump loaded,
it will serialize the data into `xml` files.
Since the data is already obtained from the SourceData API, the process
will be much faster than querying the API. This will serialize the data
in some tens of minutes.

```bash
     python -m src.soda_data.sdneo.get_sd "/app/data/xml"
```

### From the SourceData API

It will download the data from the SourceData API and serialize it into `xml` files.
It requires access and login credentials to the API.
The download process might be as long as two days.

```bash
     python -m src.soda_data.sdneo.get_sd "/app/data/xml" --api sdapi
```


## Run the tests

```bash
pip install -e .
pip install responses==0.23.0 --no-dependencies
```

```bash
coverage run --source=src -m pytest --cov src/soda_data -v tests
```

```bash
# Get the data from sd-graph
docker-compose run --rm flask python -m sdg.sdneo PUBLICSEARCH --api sdapi  # import source data public data

# Dump the data from sd-graph
docker run --rm --name neo4j-dump --env-file .env --mount type=bind,source=$PWD/data/neo4j-data,target=/data --mount type=bind,source=$PWD/dumps,target=/dumps neo4j:4.1 bin/neo4j-admin dump --database=neo4j --to=/dumps/sourcedata_v0-0-0.db.dump.`date +%Y-%m-%d-%H.%M.%S`

# Load data dump
docker run --rm --name neo4j-load --env-file .env --mount type=bind,source=$PWD/data/neo4j-data,target=/data --mount type=bind,source=$PWD/dumps,target=/dumps -it neo4j:4.1 bin/neo4j-admin load --database=neo4j --from=/dumps/<dump_filename>

```

## Note

This project has been set up using PyScaffold 4.4. For details and usage
information on PyScaffold see https://pyscaffold.org/.

[![Project generated with PyScaffold](https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold)](https://pyscaffold.org/)
