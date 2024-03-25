FROM nvcr.io/nvidia/pytorch:22.01-py3

RUN apt-get install curl build-essential -y
RUN curl -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

RUN apt-get update \
&& pip install --upgrade pip setuptools \
&& pip install --upgrade pip 

RUN pip install --upgrade pip && pip install -e .

# Clear cache
RUN apt-get clean && rm -rf /var/lib/apt/lists/*1
