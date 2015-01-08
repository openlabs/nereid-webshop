# Nereid-Webshop
#
# VERSION	3.4.0.1

FROM openlabs/tryton:3.4
MAINTAINER Prakash Pandey <prakash.pandey@openlabs.co.in>

RUN apt-get -y update

# * Setup psycopg2 since you want to connect to postgres
#   database
# * Install pillow since image-transaformation uses it
RUN apt-get -y -q install python-dev libpq-dev python-pillow gunicorn python-gevent python-psycopg2

ADD . /opt/nereid-webshop/
WORKDIR /opt/nereid-webshop/
RUN pip install -r requirements.txt

WORKDIR /opt/nereid-webshop/web

# SET data_path to a volume on the server
VOLUME /var/lib/trytond

EXPOSE 	9000
CMD ["-b", "0.0.0.0:9000", "--error-logfile", "-", "-k", "gevent", "-w", "4", "application:app"]
ENTRYPOINT ["gunicorn"]
