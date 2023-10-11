import os
from pendulum import datetime

from airflow import DAG
from airflow.operators.empty import EmptyOperator

from cosmos import DbtDag, ProjectConfig, ProfileConfig, ExecutionConfig, DbtTaskGroup
from cosmos.profiles import PostgresUserPasswordProfileMapping


AIRFLOW_CONNECTION_ID = "postgres_conn"
PSQL_SCHEMA_NAME = "dbt_test_schema"
DBT_PROJECT_NAME = "jaffle_shop"

# For SF using Private Key: https://astronomer.github.io/astronomer-cosmos/profiles/SnowflakePrivateKeyPem.html

profile_config = ProfileConfig(
    profile_name="default",
    target_name="dev",
    profile_mapping=PostgresUserPasswordProfileMapping(
        conn_id=AIRFLOW_CONNECTION_ID,    # Astronomer-Cosmos uses actual Airflow connection, instead of DBT profile
        profile_args={"schema": PSQL_SCHEMA_NAME}
    ),
)

my_dbt_dag = DbtDag(
    project_config=ProjectConfig(
        f"/usr/local/airflow/dags/dbt/{DBT_PROJECT_NAME}",
    ),
    profile_config=profile_config,
    execution_config=ExecutionConfig(
        dbt_executable_path=f"{os.environ['AIRFLOW_HOME']}/dbt_venv/bin/dbt",
    ),
    # normal dag parameters
    schedule_interval="@daily",
    start_date=datetime(2023, 1, 1),
    catchup=False,
    dag_id="lalitc_dbt_dag",
)

# with DAG(
#     dag_id="extract_dag",
#     start_date=datetime(2023, 1, 1),
#     schedule="@daily",
# ):
#     start_op = EmptyOperator(task_id="pre_dbt")

#     dbt_tg = DbtTaskGroup(
#         project_config=ProjectConfig("dags/dbt/jaffle_shop"),
#         profile_config=profile_config,
#         dbt_cmd=f"{os.environ['AIRFLOW_HOME']}/dbt_venv/bin/dbt"
#     )

#     end_op = EmptyOperator(task_id="post_dbt")

#     start_op >> dbt_tg >> end_op