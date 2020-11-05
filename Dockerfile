FROM python:3.7-slim

RUN apt-get update -y \
	&& apt-get install -y build-essential \
	&& apt-get install -y sudo


RUN sudo apt-get install -y libgflags-dev \
	&& sudo apt-get install -y zlib1g-dev \
	&& sudo apt-get install -y libbz2-dev \
	&& sudo apt-get install -y liblz4-dev \
	&& sudo apt-get install -y libzstd-dev \
	&& sudo apt-get install -y libsnappy-dev \
	&& sudo apt-get install -y librocksdb-dev

RUN pip install python-rocksdb
RUN pip install pytest

WORKDIR rockdbtest

COPY . .

CMD python -m pytest