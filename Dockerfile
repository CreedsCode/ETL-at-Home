FROM apache/airflow:2.2.0
RUN pip install stravalib
RUN pip install openpyxl
RUN /usr/local/bin/python -m pip install --upgrade pip
