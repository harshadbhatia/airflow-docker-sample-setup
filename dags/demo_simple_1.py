import os

from datetime import datetime, timedelta

from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.python_operator import PythonOperator

from airflow.providers.microsoft.azure.operators.adls_list import AzureDataLakeStorageListOperator

from azure.storage.blob import BlobServiceClient
from azure.storage.file import ContentSettings

args = {
    'owner': 'airflow',
    "start_date": days_ago(2)
}

def get_resource_reference(self, prefix):
        return '{}{}'.format(prefix, str(uuid.uuid4()).replace('-', ''))


def get_blob_reference(self, prefix='blob'):
    return get_resource_reference(prefix)


def get_config():
    host = "172.22.0.4"

    return {
        "conn_string": f'DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://{host}:10000/devstoreaccount1;',
        "container1": 'source-container',
        "container2": 'dest-container'
    }


def create_blob_service_connection():
    return BlobServiceClient.from_connection_string(get_config()['conn_string'])


def create_container():
    """This """
    config = get_config()
    client = create_blob_service_connection()
    account_info = client.get_account_information()
    
    try:
        # client
        client.create_container(config['container1'])
        client.create_container(config['container2'])
        print("="*50, 'complete')
    except Exception as e:
        print(e)



def create_files():

    config = get_config()
    client = create_blob_service_connection()

    for i in range(10):
        file_name = f'demo_{i}.txt'
        blob_client = client.get_blob_client(container=config['container1'], blob=file_name)

        print("\nUploading to Azure Storage as blob:\n\t" + file_name)

        # Upload the created file
        # with open(file_name, "rb") as data:
        blob_client.upload_blob(b"This is some dummy content")
        
    print("="*50, 'complete')



# (top-level) DAG & operators
with DAG(dag_id="demo_simple_1",
          default_args=args,
          schedule_interval=None) as dag:

    create_container = PythonOperator(
        python_callable=create_container,
        task_id='create_container'
    )

    create_files = PythonOperator(
        python_callable=create_files,
        task_id='create_10_random_files'
    )

    create_container >> create_files

if __name__ == "__main__":
    dag.cli()