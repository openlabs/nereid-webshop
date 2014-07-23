# Nereid Webshop 3.2
#
# VERSION	3.2

FROM openlabs/tryton:3.2
MAINTAINER Openlabs Technologies and Consulting (P) Ltd <info@openlabs.co.in>

# Update package repository
RUN apt-get update

# Setup environment and UTF-8 locale
ENV DEBIAN_FRONTEND noninteractive
ENV LANGUAGE en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8

# Install header files for python and postgreSQL library
RUN apt-get -y -q install libpq-dev python-dev

# Install supervisor
RUN apt-get install -y supervisor
RUN mkdir -p /var/log/supervisor

# Mount host directory
ADD . /opt/nereid-webshop

# Change the working directory
WORKDIR /opt/nereid-webshop

# Add supervisor configuration
ADD docker_files/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Install nereid webshop
RUN pip install -r requirements.txt

# Initialise the database
RUN echo admin > /.trytonpassfile
ENV TRYTONPASSFILE /.trytonpassfile

EXPOSE 5000 8000
CMD ["/usr/bin/supervisord"]
