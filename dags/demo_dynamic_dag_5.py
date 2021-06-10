import os

from datetime import datetime, timedelta

from airflow import DAG
from airflow.models import Variable
from airflow.utils.dates import days_ago

from airflow.operators.dummy import DummyOperator 
from azureP.operators.azure_az_copy_operator import AzureAZCopyOperator

args = {
    'owner': 'airflow',
    "start_date": days_ago(2)
}

DAG_ID = "demo_dynamic_dag_5"

config = Variable.get(DAG_ID, deserialize_json=True)

# (top-level) DAG & operators
with DAG(dag_id=DAG_ID,
          default_args=args,
          schedule_interval=None) as dag:

    start = DummyOperator(task_id="start")
    end = DummyOperator(task_id="end")

    for i in range(10):

        copy_blob = AzureAZCopyOperator(
            task_id=f'copy_task_{i}',
            azure_source_conn_id='azure_blob',
            azure_dest_conn_id='azure_blob',
            source_storage=config['source_storage'],
            source_file_name=f"demo_{i}.txt",
            source_container=config['source_container'],
            dest_container=config['dest_container']     
        )

        start >> copy_blob >> end
    
    

    # end.set_upstream(copy_blob)
    

if __name__ == "__main__":
    dag.cli()