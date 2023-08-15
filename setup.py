"""
    Setup file for soda-data.
    Use setup.cfg to configure your project.

    This file was generated with PyScaffold 4.4.
    PyScaffold helps you to put up the scaffold of your new Python project.
    Learn more under: https://pyscaffold.org/
"""
from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

if __name__ == "__main__":
    try:
        setup(
            # use_scm_version={"version_scheme": "no-guess-dev"},
            # use_scm_version=True,
            # setup_requires=['setuptools_scm'],
            name="soda_data",
            version="1.0.0",
            python_requires=">=3.8",
            author="Dr. Jorge Abreu Vicente, Thomas Lemberger",
            author_email="source_data@embo.org",
            description="""The largest annotated biomedical corpus for machine learning and AI in the publishing context.""",
            long_description=long_description,
            long_description_content_type="text/markdown",
            url="https://github.com/source-data/soda-data",
            packages=["soda_data"],
            install_requires=[
                "torch",
                "transformers==4.20",
                "datasets~=2.10.0",
                "nltk",
                "scikit-learn",
                "python-dotenv",
                "seqeval",
                "lxml",
                "neo4j",
                "responses<0.19",
                "py2neo==2021.2.3",
                "beautifulsoup4==4.10.0",
                "sentence-transformers==2.2.2"
            ],
            classifiers=[
                # full list: https://pypi.org/pypi?%3Aaction=list_classifiers
                "Development Status :: 1 - Planning",
                "Intended Audience :: Science/Research",
                "Programming Language :: Python :: 3.6",
                "License :: Other/Proprietary License",
                "Operating System :: MacOS :: MacOS X",
                "Operating System :: POSIX",
                "Topic :: Scientific/Engineering :: Artificial Intelligence",
                "Topic :: Scientific/Engineering :: Bio-Informatics",
                "Topic :: Software Development :: Libraries",
            ],
        )
    except:  # noqa
        print(
            "\n\nAn error occurred while building the project, "
            "please ensure you have the most updated version of setuptools, "
            "setuptools_scm and wheel with:\n"
            "   pip install -U setuptools setuptools_scm wheel\n\n"
        )
        raise
