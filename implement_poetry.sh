#!/bin/sh
echo "-------------------Start Implementing Poetry--------------------"

# install poetry
pip install poetry
poetry config virtualenvs.create false
printf 'resources_api\n\nThis is Resources API for OC\nOC_Contributors\nMIT\n^3.7\nno\nno\n\n' | poetry init
poetry add `cat requirements.txt`

echo "-----------------------Editing Dockerfile-----------------------"
#Edit Dockerfile
sed -i 's/ADD requirements.txt requirements.txt/COPY pyproject.toml poetry.lock .\//' Dockerfile
sed -i '/pip install --upgrade pip/ s/$/ \\/'  Dockerfile

sed -i '/pip install --upgrade pip \\/ a\
    && pip install poetry \\\
    && poetry config virtualenvs.create false' Dockerfile

sed -i 's/RUN pip install -r requirements.txt/RUN poetry install/' Dockerfile

echo "------------------Finished Implementing Poetry------------------"
