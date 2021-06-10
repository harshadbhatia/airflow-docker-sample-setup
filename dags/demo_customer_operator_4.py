import os

from datetime import datetime, timedelta

from airflow import DAG
from airflow.models import Variable
from airflow.utils.dates import days_ago

from azureP.operators.azure_az_copy_operator import AzureAZCopyOperator

args = {
    'owner': 'airflow',
    "start_date": days_ago(2)
}

DAG_ID = "demo_custom_operator_4"

config = Variable.get(DAG_ID, deserialize_json=True)

# (top-level) DAG & operators
with DAG(dag_id=DAG_ID,
          default_args=args,
          schedule_interval=None) as dag:

    copy_blob = AzureAZCopyOperator(
        task_id='copy_task',
        azure_source_conn_id='azure_blob',
        azure_dest_conn_id='azure_blob',
        source_storage=config['source_storage'],
        source_files=config['source_files'],
        source_container=config['source_container'],
        dest_container=config['dest_container']     
    )

    copy_blob

if __name__ == "__main__":
    dag.cli()