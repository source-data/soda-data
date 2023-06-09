FROM nvcr.io/nvidia/pytorch:22.01-py3

RUN apt-get install curl build-essential -y
RUN curl -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

RUN apt-get update \
&& pip install --upgrade pip setuptools \
&& pip install --upgrade pip \
# reinstall numpy with version compatible with nvcr.io/nvidia/pytorch:22.01-py3
&& pip install numpy==1.22.2 \
&& pip install python-dotenv==0.15.0 \
&& pip install nltk==3.5 \
&& pip install scikit-learn==0.24.0 \
&& pip install transformers==4.20.0 \
&& pip install datasets==1.17.0 \
&& pip install seqeval==1.2.2 \
# && pip install celery==5.0.5 \
# && pip install flower==0.9.7 \
# && pip install spacy==2.3.5 \
&& pip install lxml==4.6.2 \
&& pip install neo4j==4.1.1 \
# && python -m spacy download en_core_web_sm \
# && pip install ipywidgets \
&& pip install neotools==0.3.3 \
&& pip install responses==0.18.0
# optional for plotting
# RUN pip install plotly

# Clear cache
RUN apt-get clean && rm -rf /var/lib/apt/lists/*1
