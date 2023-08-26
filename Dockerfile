FROM python:3.10-bullseye
LABEL author=Dynamical_LR_TEAM
RUN echo "Building project... Relax and get some 🍺"

# Root user credentials 
ARG ROOT_USER=python_user

# Environment Project Variables
ENV PYTHONUNBUFFERED=0

# Creating custom user
RUN useradd -ms /bin/bash ${ROOT_USER}
RUN usermod -aG sudo ${ROOT_USER}

# Initializing working directory 
WORKDIR /project/dir/${ROOT_USER}

# copying project source 

COPY ./env_vars ./env_vars
COPY ./proj_requirements/ ./
COPY ./models ./models
COPY ./key_generator ./key_generator
COPY ./photos ./photos
COPY ./analytics ./analytics
COPY ./parsers ./parsers
COPY ./rest ./rest
COPY ./tests ./tests
COPY __init__.py ./__init__.py
COPY entrypoint.sh ./entrypoint.sh

# updating pip installer and installing gcc lib for more reliable project 
# compilation

RUN pip install --upgrade pip
RUN apt-get install gcc

# Installing Production requirements inside python project
RUN pip install -r prod_requirements.txt 

# Upgrading Python Package
RUN pip install 'fastapi[all]' --upgrade

# Giving Permissions for running entrypoint shell script
RUN chmod +x entrypoint.sh
ENTRYPOINT ["sh", "entrypoint.sh"]