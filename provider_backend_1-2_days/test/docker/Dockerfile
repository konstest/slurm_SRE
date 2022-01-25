FROM python:3.8-slim-buster


COPY requirements.test.txt /root/provider_backend/requirements.test.txt
RUN ls /root/provider_backend
RUN pip3 install -r /root/provider_backend/requirements.test.txt

ENV TEST_POSTGRES_HOST postgresql

COPY ./ /root/provider_backend
RUN chmod 0755 /root/provider_backend/test/docker/entrypoint.sh
ENTRYPOINT ["/root/provider_backend/test/docker/entrypoint.sh"]
