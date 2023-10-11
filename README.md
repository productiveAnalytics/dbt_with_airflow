Overview
========

Welcome to Astronomer! This project was generated after you ran 'astro dev init' using the Astronomer CLI. This readme describes the contents of the project, as well as how to run Apache Airflow on your local machine.

Setup for DBT with Airflow
==========================

Install PostgreSQL:
Search for PostgreSQL version
```bash
$ brew search postgresql
```
or 
```bash
$ brew formulae | grep  postgresql@
```
Install
```
brew install postgresql@14
```

To avoid conflicting with Astronomer Airlfow's internal PostgreSQL, update PSQL port from 5432 to 54321 
```
export POSTGRE_SQL_VERSION=14
export POSTGRE_SQL_HOME="${HOMEBREW_ROOT}/opt/postgresql@${POSTGRE_SQL_VERSION}"
export PATH="${POSTGRE_SQL_HOME}/bin:$PATH"

export LDFLAGS="-L${POSTGRE_SQL_HOME}/lib"
export CPPFLAGS="-I${POSTGRE_SQL_HOME}/include"

# /opt/homebrew/var/postgresql@14
export PGDATA="${HOMEBREW_ROOT}/var/postgresql@${POSTGRE_SQL_VERSION}"
export PGPORT=54321
```

Note: For homebrew installed PSQL, need to update ${PGDATA}/postgresql.conf (because PGPORT does not get considered for port)

Start PostgreSQL as service and confirm
```
brew services start postgresql@${POSTGRE_SQL_VERSION}
brew services list
nc -vz localhost ${PGPORT}
```

Create database "dbt_test_db" and schema "dbt_test_schema"
Using DBeaver, Create user "dbt_user" and assign roles to allow to be superuser, db creation, etc.

----

Install Astronomer: ```brew install astro```
Check Astronomer: ```astro version```

Initialize project: ```astro dev init```

Install packages required for astronomer-cosmos's underlying packages
```
# packages.txt
gcc
python3-dev
```

Install Python package, in requirements.txt add "astronomer-cosmos[dbt.all]" or specific db dapter
```
astronomer-cosmos[dbt.postgres]
```

Copy sample dbt repo under dags/dbt/ folder
```
git clone https://github.com/dbt-labs/jaffle_shop.git
```

dbt_with_airflow
 |___ dags
    |___ dbt
       |___jaffle_shop

Create a folder macros in jaffle_shop and generate drop_tables.sql
```
# macros/drop_table.sql
{%- macro drop_table(table_name) -%}
    {%- set drop_query -%}
        DROP TABLE IF EXISTS {{ target.schema }}.{{ table_name }} CASCADE
    {%- endset -%}
    {% do run_query(drop_query) %}
{%- endmacro -%}

``` 

Create new Astronomer specific file "docker-compose.override.yml"
```
# Allow Astroner airflow to automatically reload the DAGs
version: "3.1"
services:
  scheduler:
    volumes:
      - ./dbt:/usr/local/airflow/dbt:rw

  webserver:
    volumes:
      - ./dbt:/usr/local/airflow/dbt:rw

  triggerer:
    volumes:
      - ./dbt:/usr/local/airflow/dbt:rw
```

Create the file "dbt-requirements.txt" 
(Note: use the same version as that of installed dbt-core and dbt-postgres)
```
astronomer-cosmos==1.1.3
dbt-core==1.5.4
dbt-postgres==1.5.4
```

Append the following in existing Dockefile
```
# install dbt into a venv to avoid package dependency conflicts
WORKDIR "/usr/local/airflow"
COPY dbt-requirements.txt ./
RUN python -m virtualenv dbt_venv && source dbt_venv/bin/activate && \
    pip install --no-cache-dir -r dbt-requirements.txt && deactivate
```

MUST DO: 
As the Astronomer-Cosmos works with actual Airflow connection, instead of DBT's profile.yml, setup PostgreSQL connection in Airflow Admin UI
TIP: 
1) Enable testing of Airflow connection by adding AIRFLOW__CORE__TEST_CONNECTION=Enabled to the .env file for Docker
2) As the Astronomer Airflow is dockerized, if the PostgreSQL is on localhost, while setting Airflow connection use "host.docker.internal" instead of "localhost"


Project Contents
================

Your Astro project contains the following files and folders:

- dags: This folder contains the Python files for your Airflow DAGs. By default, this directory includes two example DAGs:
    - `example_dag_basic`: This DAG shows a simple ETL data pipeline example with three TaskFlow API tasks that run daily.
    - `example_dag_advanced`: This advanced DAG showcases a variety of Airflow features like branching, Jinja templates, task groups and several Airflow operators.
- Dockerfile: This file contains a versioned Astro Runtime Docker image that provides a differentiated Airflow experience. If you want to execute other commands or overrides at runtime, specify them here.
- include: This folder contains any additional files that you want to include as part of your project. It is empty by default.
- packages.txt: Install OS-level packages needed for your project by adding them to this file. It is empty by default.
- requirements.txt: Install Python packages needed for your project by adding them to this file. It is empty by default.
- plugins: Add custom or community plugins for your project to this file. It is empty by default.
- airflow_settings.yaml: Use this local-only file to specify Airflow Connections, Variables, and Pools instead of entering them in the Airflow UI as you develop DAGs in this project.

Deploy Your Project Locally
===========================

1. Start Airflow on your local machine by running 'astro dev start'.

This command will spin up 4 Docker containers on your machine, each for a different Airflow component:

- Postgres: Airflow's Metadata Database
- Webserver: The Airflow component responsible for rendering the Airflow UI
- Scheduler: The Airflow component responsible for monitoring and triggering tasks
- Triggerer: The Airflow component responsible for triggering deferred tasks

2. Verify that all 4 Docker containers were created by running 'docker ps'.

Note: Running 'astro dev start' will start your project with the Airflow Webserver exposed at port 8080 and Postgres exposed at port 5432. If you already have either of those ports allocated, you can either [stop your existing Docker containers or change the port](https://docs.astronomer.io/astro/test-and-troubleshoot-locally#ports-are-not-available).

3. Access the Airflow UI for your local Airflow project. To do so, go to http://localhost:8080/ and log in with 'admin' for both your Username and Password.

You should also be able to access your Postgres Database at 'localhost:5432/postgres'.

Deploy Your Project to Astronomer
=================================

If you have an Astronomer account, pushing code to a Deployment on Astronomer is simple. For deploying instructions, refer to Astronomer documentation: https://docs.astronomer.io/cloud/deploy-code/

Contact
=======

The Astronomer CLI is maintained with love by the Astronomer team. To report a bug or suggest a change, reach out to our support.
