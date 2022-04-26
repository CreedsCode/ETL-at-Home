FROM apache/airflow:2.2.0

LABEL Maintainer="contact@creedscode.cc"
LABEL org.opencontainers.image.source="https://github.com/CreedsCode/ETL-at-Home"

RUN pip install stravalib
RUN pip install openpyxl
RUN /usr/local/bin/python -m pip install --upgrade pip
