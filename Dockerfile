FROM python:3.8-alpine

WORKDIR /usr/app

COPY ./requirements.txt .

# We don't need to use a venv in a container.
# RUN ['python3', '-m', 'venv', '.ve', '&&', 'source', '.ve/bin/activate']

RUN ['python3', '-m', 'pip', 'install', '-r', 'requirements.txt']

COPY . .

CMD './setup.py'
