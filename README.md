<!-- [![Built Status](https://api.cirrus-ci.com/github/<USER>/soda-data.svg?branch=main)](https://cirrus-ci.com/github/<USER>/soda-data)
[![ReadTheDocs](https://readthedocs.org/projects/soda-data/badge/?version=latest)](https://soda-data.readthedocs.io/en/stable/) -->
<!-- [![Coveralls](https://img.shields.io/coveralls/github/drAbreu/soda-data/main.svg)](https://coveralls.io/r/drAbreu/soda-data) -->
<!-- [![Test status](https://github.com/source-data/soda-data/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/source-data/soda-data/actions/workflows/ci.yml)
[![license](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)
[![CodeFactor](https://www.codefactor.io/repository/github/source-data/soda-data/badge)](https://www.codefactor.io/repository/github/source-data/soda-data)
[![HuggingFace badge](https://img.shields.io/badge/%F0%9F%A4%97HuggingFace-Join-yellow)](https://huggingface.co/EMBO) -->
<!-- [![PyPI-Server](https://img.shields.io/pypi/v/soda-data.svg)](https://pypi.org/project/soda-data/) -->
<!-- [![Conda-Forge](https://img.shields.io/conda/vn/conda-forge/soda-data.svg)](https://anaconda.org/conda-forge/soda-data) -->
<!-- [![Monthly Downloads](https://pepy.tech/badge/soda-data/month)](https://pepy.tech/project/soda-data) -->
<!-- [![Twitter](https://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Twitter)](https://twitter.com/soda-data) -->
<p align="center">
    <a href="https://arxiv.org/abs/2310.20440">
        <img alt="ArXiv paper" src="https://img.shields.io/badge/cs.CL-2310.20440-b31b1b?logo=arxiv&logoColor=red">
    </a>
    <a href="https://github.com/source-data/soda-data/actions/workflows/ci.yml">
        <img alt="Build" src="https://github.com/source-data/soda-data/actions/workflows/ci.yml/badge.svg?branch=master">
    </a>
    <a href="https://github.com/source-data/soda-data/blob/master/LICENSE">
        <img alt="GitHub" src="https://img.shields.io/github/license/source-data/soda-data.svg?color=blue">
    </a>
    <a href="https://www.codefactor.io/repository/github/source-data/soda-data">
        <img alt="CodeFactor" src="https://www.codefactor.io/repository/github/source-data/soda-data/badge">
    </a>
    <a href="https://huggingface.co/EMBO">
        <img alt="GitHub release" src="https://img.shields.io/badge/%F0%9F%A4%97HuggingFace-Join-yellow">
    </a>
    <a href="https://doi.org/10.57967/hf/0495">
        <img alt="GitHub release" src="http://img.shields.io/badge/DOI-10.57967/hf/0495-B31B1B.svg">
    </a>

</p>

# SourceData Dataset

> The largest annotated biomedical corpus for machine learning and AI in the publishing context.

SourceData is the largest annotated biomedical dataset for NER and NEL.
It is unique on its focus on the core of scientific evidence:
figure captions. It is also unique on its real-world configuration, since it does not
present isolated sentences out of more general context. It offers full annotated figure
captions that can be further enriched in context using full text, abstracts, or titles.
The goal is to extract the nature of the experiments on them described.
SourceData presents also its uniqueness by labelling the causal relationship
between biological entities present in experiments, assigning experimental roles
to each biomedical entity present in the corpus.

SourceData consistently annotates
nine different biological entities (genes, proteins, cells, tissues,
subcellular components, species, small molecules, and diseases). It is
the first dataset annotating experimental assays
and the roles played on them by the biological entities.
Each entity is linked to their correspondent ontology, allowing
for entity disambiguation and NEL.

<!-- pyscaffold-notes -->

## Cite SourceData

```latex

@ARTICLE{2023arXiv231020440A,
       author = {{Abreu-Vicente}, Jorge and {Sonntag}, Hannah and {Eidens}, Thomas and {Lemberger}, Thomas},
        title = {The SourceData-NLP dataset: integrating curation into scientific publishing for training large language models},
      journal = {arXiv e-prints},
     keywords = {Computer Science - Computation and Language},
         year = 2023,
        month = oct,
          eid = {arXiv:2310.20440},
        pages = {arXiv:2310.20440},
          doi = {10.48550/arXiv.2310.20440},
archivePrefix = {arXiv},
       eprint = {2310.20440},
 primaryClass = {cs.CL},
       adsurl = {https://ui.adsabs.harvard.edu/abs/2023arXiv231020440A},
      adsnote = {Provided by the SAO/NASA Astrophysics Data System}
}

@misc {embo_2023,
	author       = { Abreu-Vicente, J. \& Lemberger, T. },
	title        = { The SourceData dataset},
	year         = 2023,
	url          = { https://huggingface.co/datasets/EMBO/SourceData },
	doi          = { 10.57967/hf/0495 },
	publisher    = { Hugging Face }
}

@article {Liechti2017,
     author = {Liechti, Robin and George, Nancy and Götz, Lou and El-Gebali, Sara and Chasapi, Anastasia and Crespo, Isaac and Xenarios, Ioannis and Lemberger, Thomas},
     title = {SourceData - a semantic platform for curating and searching figures},
     year = {2017},
     volume = {14},
     number = {11},
     doi = {10.1038/nmeth.4471},
     URL = {https://doi.org/10.1038/nmeth.4471},
     eprint = {https://www.biorxiv.org/content/early/2016/06/20/058529.full.pdf},
     journal = {Nature Methods}
}
```

## First time installation

Clone the repository to your computer and follow the following steps.
First, take a look to the `.env.example` file and generate your own,
with your persnoal values in an `.env` file.

```bash
docker-compose build --force-rm --no-cache
docker-compose down --volumes # to clean the content of the volumes
docker-compose up -d

# Wait about 30 seconds until neo4j is up and running
```

> Make sure to configure <YOUR_PASS> in the .env file of the .repository

## Obtaining the data:

This repository is used to generate ready-to-go ML / AI data compatible with the
🤗 Transformers library. Indeed, the data generated can be found in the
[`EMBO/SourceData`](https://huggingface.co/datasets/EMBO/SourceData) repository.

If you need to generate data that is not oficially supported yet, please contact us
to generated or send a pull request to add that data to our repository.

We currently support data processing for the tasks of `TokenClassification`.
Namely, for NER, semantic roles, and panelization of figure captions.

We have added an `api` module intended to enrich the SourceData dataset with any external
data, either from ontologies or Europe PMC.

The repository has everything needed to retrieve the data from the SourceData API.
There are to ways to do so:

     1. Using your own SourceData API account
     2. Using the publically available `neo4j` dumps ([`EMBO/SourceData`](https://huggingface.co/datasets/EMBO/SourceData)).

> The neo4j option is currently not supported for the new MAC processor architecture

The repository will serialize the data into `xml` format to then convert it into
ML ready format. It offers the option of automatically upload the generated data to the 🤗 Hub,
given that a valid token is provided in the `.env` file.

#### Instantiating a neo4j database and loading data on it

We periodically upload neo4j data dumps of the SourceData API to our 🤗 Hub,
[EMBO/SourceData](https://huggingface.co/datasets/EMBO/SourceData/tree/main/neo_dumps).

These dumps can be downloaded and used to generate a local neo4j instance in
the docker container using the following steps:

```bash
#Download the neo4j dump
# Load data dump
docker-compose down

# If you run into permission problems add sudo or use chmod to change the permissions in ./data
mkdir data/neo_dumps
# Check in the HuggingFace repo for the available neo4j dumps
wget -P $PWD/data/neo_dumps https://huggingface.co/datasets/EMBO/SourceData/resolve/main/neo_dumps/sourcedata_v1-0-0.db.dump.2023-03-29-15.07.42

docker run --rm --name neo4j-load \
     --env-file .env \
     --mount type=bind,source=$PWD/data/neo4j-data,target=/data \
     --mount type=bind,source=$PWD/data/neo_dumps,target=/dumps \
     -it neo4j:4.4 bin/neo4j-admin load \
     --database=neo4j --from=/dumps/sourcedata_v1-0-0.db.dump.2023-03-29-15.07.42 \
     --force # Note that this will overwrite any content ! ! ! ! !
```

> To make it work on new Apple Mac, we need to use neo4j >=4.4 which is more recent than the version used for some of the dumps. This is the reason for the warning _"The loaded database is not on the latest format (current:SF4.0.0, latest:SF4.3.0). Set dbms.allow_upgrade=true to enable migration."_ indicates that the `NEO4J_dbms_allow__upgrade=true` should be set. This is included in .env file and set in the docker-compose file.

```bash
docker compose up
```

### From a Neo4j dump

If a neo4j instance is in place and with a SourceData dump loaded,
it will serialize the data into `xml` files.
Since the data is already obtained from the SourceData API, the process
will be much faster than querying the API. This will serialize the data
in some tens of minutes.

```bash
     python -m src.soda_data.sdneo.get_sd "/app/data/xml"
```

### Loading data directly from the SourceData API

It will download the data from the SourceData API and serialize it into `xml` files.
It requires access and login credentials to the API.
The download process might be as long as two days.

```bash
     python -m src.soda_data.sdneo.get_sd "/app/data/xml" --api sdapi
```

## Upload data to 🤗 Hub

The datasets generated with this repository can be automatically uploaded to
the 🤗 Hub to be used in the 🤗 datasets or transformers libraries.
Note that a valid API token is needed.

The token can be configured in two ways:
1. Specifying `HF_TOKEN="hf_<VALID_TOKEN>"` in the `.env` file
2. Passing the option `--token "hf_<VALID_TOKEN>"` to the script call

### Upload ML / AI ready datasets

It uploads a folder containing the files ready for machine learning.
By default it will be done anytime a dataprocessing is run. It generates a
file versioning and uploads all the data to a folder of name vx.y.z in
the repository.

#### Upload the `TokenClassification` datasets

The `TokenClassification` datasets can be directly processed from the `xml` files.
a simple command will generate and upload them to the 🤗 Hub.

```bash
     # From outside of the docker container
     docker-compose exec -T nlp \
          python -m soda_data.dataproc.create_token_classification \
          --destination_dir "/path/to/local/folder" \
          --version "x.y.z" \
          --repo_name "HF_USER/repo" \
          --token "HF_TOKEN" \ #  This is not needed if the token is configured in the .env file
          --patch_generic # Applies the generic patch to the dataset

     # From inside the docker container
     python -m soda_data.dataproc.create_token_classification \
          --destination_dir "/path/to/local/folder" \
          --version "x.y.z" \
          --repo_name "HF_USER/repo" \
          --token "HF_TOKEN" \ #  This is not needed if the token is configured in the .env file
          --patch_generic # Applies the generic patch to the dataset
```

The procedure will generate a folder `vx.y.z` inside the folder `token_classification`.
In this folder, five others will be created, each for one of the different
fine-tuning tasks intended: `panelization`, `ner`, `roles_gene`, `roles_small_mol`,
and `roles_multi`. We show below ane xample schema of how the data would be organized.

```
     EMBO/SourceData
     |--SourceData.py (data loader script)
     |--README.md
     |--neo_dumps
     |    |
     |    |--neo_file.db.dump.version
     |
     |--token_classification
     |   |--panelization
     |   |  |----v1.0.0
     |   |  |        |---train.jsonl
     |   |  |        |---validation.jsonl
     |   |  |        |---test.jsonl
     |   |  |----v1.1.0
     |   |  |        |---train.jsonl
     |   |  |        |---validation.jsonl
     |   |  |        |---test.jsonl
     |   |
     |   |--ner
     |   |  |----v1.0.0
     |   |  |        |---train.jsonl
     |   |  |        |---validation.jsonl
     |   |  |        |---test.jsonl
     |   |  |----v1.1.0
     |   |  |        |---train.jsonl
     |   |  |        |---validation.jsonl
     |   |  |        |---test.jsonl
     |   |
     |   |--roles_gene
     |   |  |----v1.0.0
     |   |  |        |---train.jsonl
     |   |  |        |---validation.jsonl
     |   |  |        |---test.jsonl
     |   |  |----v1.1.0
     |   |  |        |---train.jsonl
     |   |  |        |---validation.jsonl
     |   |  |        |---test.jsonl
     |   |
     |   |--roles_small_mol
     |   |  |----v1.0.0
     |   |  |        |---train.jsonl
     |   |  |        |---validation.jsonl
     |   |  |        |---test.jsonl
     |   |  |----v1.1.0
     |   |  |        |---train.jsonl
     |   |  |        |---validation.jsonl
     |   |  |        |---test.jsonl
     |   |
     |   |--roles_multi
     |   |  |----v1.0.0
     |   |  |        |---train.jsonl
     |   |  |        |---validation.jsonl
     |   |  |        |---test.jsonl
     |   |  |----v1.1.0
     |   |  |        |---train.jsonl
     |   |  |        |---validation.jsonl
     |   |  |        |---test.jsonl

```

#### Upload neo4j data dumps

It will upload a folder containing one or several files. It can be used for neo dumps
or for any other kind of file:

```bash
     # From outside of the docker container
     docker-compose exec -T nlp \
          python -m soda_data.dataproc.upload_neo_dump \
          --local_folder "/path/to/local/folder" \
          --repo_name "HF_USER/repo" \
          --token "HF_TOKEN" #  This is not needed if the token is configured in the .env file

     # From inside the docker container
     python -m soda_data.dataproc.upload_neo_dump \
          --local_folder "/path/to/local/folder" \
          --repo_name "HF_USER/repo" \
          --token "HF_TOKEN" #  This is not needed if the token is configured in the .env file
```
docker-compose exec -T nlp \
          python -m soda_data.dataproc.upload_neo_dump \
          --local_folder "/data/json/token_classification" \
          --repo_name "EMBO/SourceData"  \
          --path_repo "token_classification"


## Informstion extraction data for LLMs

This data can be generated using the `cypher` queries in `src/soda_data/sdneo/neo_queries.py`. The data generated in this way will be added to the `EMBO/SourceData` repository in HuggingFace🤗, in the folder `information_extraction`.

## Contribution to the code

First, make sure to install the package on a development mode. Inside the container type:

```bash
     pip install -e .
```


## Run the tests

```bash
     pip install -e .
     coverage run --source=src -m pytest --cov src/soda_data -v tests
```

## Internal memorandum

```bash
     # Get the data from sd-graph
     docker-compose run --rm flask python -m sdg.sdneo PUBLICSEARCH --api sdapi  # import source data public data

     # Dump the data from sd-graph
     docker run --rm --name neo4j-dump --env-file .env --mount type=bind,source=$PWD/data/neo4j-data,target=/data --mount type=bind,source=$PWD/dumps,target=/dumps neo4j:4.1 bin/neo4j-admin dump --database=neo4j --to=/dumps/sourcedata_v2-0-2.db.dump.`date +%Y-%m-%d-%H.%M.%S`

```

## Note

This project has been set up using PyScaffold 4.4. For details and usage
information on PyScaffold see https://pyscaffold.org/.

[![Project generated with PyScaffold](https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold)](https://pyscaffold.org/)
