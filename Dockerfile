FROM python:3.8

ENV PYTHONUNBUFFERED 1

RUN pip install pipenv

WORKDIR /openstack-glance-exporter

ARG CI_REGISTRY_USER
ARG CI_JOB_TOKEN
ARG CI_SERVER_HOST
RUN git config --global url."https://$CI_REGISTRY_USER:$CI_JOB_TOKEN@$CI_SERVER_HOST/".insteadOf https://$CI_SERVER_HOST/

ADD Pipfile .
ADD Pipfile.lock .
RUN pipenv install --system

RUN git config --global --unset url."https://$CI_REGISTRY_USER:$CI_JOB_TOKEN@$CI_SERVER_HOST/".insteadOf https://$CI_SERVER_HOST/

ADD . .

ENTRYPOINT [ "python3", "app.py" ]
