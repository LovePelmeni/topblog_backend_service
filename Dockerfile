FROM python:3.10-bullseye
LABEL author=kirklimushin@gmail.com 
RUN echo "Building project... Relax and get some 🍺"

# Root user credentials 
ARG ROOT_USER=python_user

# Environment Project Variables
ENV POETRY_VIRTUALENVS_CREATE=false
ENV PYTHONUNBUFFERED=0

# Creating custom user
RUN useradd -ms /bin/bash ${ROOT_USER}
RUN usermod -aG sudo ${ROOT_USER}

# Initializing working directory 
WORKDIR /project/dir/${ROOT_USER}

# copying project source 

COPY ./src ./src
COPY ./proj_requirements/prod_requirements.txt ./
COPY ./definitions.py ./
COPY ./rest ./rest
COPY ./tests ./tests
COPY __init__.py ./__init__.py
COPY deployment/entrypoint.sh ./
COPY ./tox.ini ./

# updating pip installer and installing gcc lib for more reliable project 
# compilation
RUN pip install --upgrade pip && apt-get install gcc

# installing poetry package manager
RUN pip install poetry

RUN poetry install --no-dev && poetry export --format=requirements.txt \
--output=prod_requirements.txt --without-hashes

RUN pip install -r prod_requirements.txt && pip install 'fastapi[all]' --upgrade

RUN chmod +x definitions.py
RUN chmod +x entrypoint.sh
RUN chmod +x definitions.py

RUN python definitions.py
ENTRYPOINT ["sh", "entrypoint.sh"]