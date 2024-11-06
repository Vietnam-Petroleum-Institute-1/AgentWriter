FROM postgres:13

# Set environment variables for PostgreSQL user credentials and database
ENV POSTGRES_PASSWORD=postgres
ENV POSTGRES_USER=postgres
ENV POSTGRES_DB=agent_notebook

# Set the working directory for initialization scripts
WORKDIR /docker-entrypoint-initdb.d/

# Copy the SQL backup file to the initialization directory
COPY ini_backup.sql /docker-entrypoint-initdb.d/

# Ensure listen_addresses is configured for all IPs in a temporary location
RUN sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" /usr/share/postgresql/postgresql.conf.sample

# Copy the modified configuration file to `/etc/postgresql/`, where PostgreSQL will look for it at runtime
RUN mkdir -p /etc/postgresql/ && \
    cp /usr/share/postgresql/postgresql.conf.sample /etc/postgresql/postgresql.conf

# Set PostgreSQL to use the modified config by adding it as an environment variable
ENV POSTGRES_INITDB_ARGS="--config-file=/etc/postgresql/postgresql.conf"

# Build image and run container
# docker build -t my_postgres_image .
# docker run -d -p 5432:5432 --name postgres_container my_postgres_image

