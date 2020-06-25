FROM ubuntu:18.04 AS codeql_base
LABEL maintainer="Github codeql team"
    
# install/update basics and python
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    	software-properties-common \
    	vim \
    	curl \
    	wget \
    	git \
    	build-essential \
    	unzip \
    	apt-transport-https \
        python3.8 \
    	python3-venv \
    	python3-pip \
    	python3-setuptools \
        python3-dev \
    	gnupg \
    	g++ \
    	make \
    	gcc \
    	apt-utils \
        rsync \
    	file \
    	gettext && \
        apt-get clean

# Install codeQL 2.2.3
ENV CODEQL_HOME /usr/local/codeql-home
RUN mkdir -p ${CODEQL_HOME} \
${CODEQL_HOME}/codeql-cli \
${CODEQL_HOME}/codeql-repo \
${CODEQL_HOME}/codeql-go-repo
RUN wget -q https://github.com/github/codeql-cli-binaries/releases/download/v2.2.3/codeql-linux64.zip -O /tmp/codeql_linux.zip && \
    unzip /tmp/codeql_linux.zip -d ${CODEQL_HOME}/codeql-cli && \
    rm /tmp/codeql_linux.zip

# get the latest codeql queries
RUN git clone https://github.com/github/codeql ${CODEQL_HOME}/codeql-repo
RUN git clone https://github.com/github/codeql-go ${CODEQL_HOME}/codeql-go-repo

# Clone our setup and run scripts
#RUN git clone https://github.com/github/codeql-docker /usr/local/startup_scripts
RUN mkdir -p /usr/local/startup_scripts
COPY docker/setup.py /usr/local/startup_scripts/
COPY docker/requirements.txt /usr/local/startup_scripts/
RUN pip3 install --upgrade pip \
    && pip3 install -r $/usr/local/startup_scripts/requirements.txt

ENV PATH="${CODEQL_HOME}/codeql:${PATH}"

ENTRYPOINT ["/"]