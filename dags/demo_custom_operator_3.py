import os

from datetime import datetime, timedelta

from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.models import Variable
from airflow.operators.python_operator import PythonOperator

from azureP.operators.azure_blob_copy_operator import AzureBlobCopyOperator

args = {
    'owner': 'airflow',
    "start_date": days_ago(2)
}

DAG_ID = "demo_custom_operator_3"

config = Variable.get(DAG_ID, deserialize_json=True)

# (top-level) DAG & operators
with DAG(dag_id=DAG_ID,
          default_args=args,
          schedule_interval=None) as dag:

    copy_blob = AzureBlobCopyOperator(
        task_id='copy_task',
        azure_source_conn_id='azure_blob',
        azure_dest_conn_id='azure_blob',
        source_storage=config['source_storage'],
        source_file_name=config['source_file_name'],
        source_container=config['source_container'],
        dest_file_name=config['dest_file_name'],
        
    )

    copy_blob

if __name__ == "__main__":
    dag.cli()