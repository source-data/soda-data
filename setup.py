"""
    Setup file for soda-data.
    Use setup.cfg to configure your project.

    This file was generated with PyScaffold 4.4.
    PyScaffold helps you to put up the scaffold of your new Python project.
    Learn more under: https://pyscaffold.org/
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

if __name__ == "__main__":
    try:
        setup(
            use_scm_version={"version_scheme": "no-guess-dev"},
            name="soda_data",
            version="0.1.0",
            python_requires=">=3.8",
            author="Dr. Jorge Abreu Vicente, Thomas Lemberger",
            author_email="source_data@embo.org",
            description="""The largest annotated biomedical corpus for machine learning and AI in the publishing context.""",
            long_description=long_description,
            long_description_content_type="text/markdown",
            url="https://github.com/source-data/soda-data",
            packages=find_packages(),
            install_requires=[
                "numpy==1.22.2",
                "torch",
                "transformers==4.20",
                "datasets~=2.10.0",
                "nltk==3.5",
                "scikit-learn==0.24.0",
                "python-dotenv==0.15.0",
                "seqeval==1.2.2",
                "lxml==4.6.2",
                "neo4j==5.16.0",
                "responses<0.19",
                "py2neo==2021.2.4",
                # "jupyterlab",
                # "ipykernel",
                # # for jupyter lab
                # "ipywidgets",
                # "jupyterlab-widgets",
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
