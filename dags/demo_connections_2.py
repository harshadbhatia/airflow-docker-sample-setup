import json 

from airflow import DAG, settings
from airflow.utils.dates import days_ago
from airflow.operators.python_operator import PythonOperator

from airflow.models import Connection

args = {
    'owner': 'airflow',
    "start_date": days_ago(2)
}


def create_connections():
    host = "172.22.0.4"
    connections = [
        {
            "id": "azure_blob",
            "description": "azure connection for blob storage",
            "host": host,
            "login": "",
            "schema": "devstoreaccount1",
            "password": "Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==",
            "port": "10000",
            "type": "wasb",
            "extras": {
                "extra__wasb__DefaultEndpointsProtocol": "http"
            }
        }
    ]


    for connection in connections:
        new_conn = Connection(
            conn_id=connection['id'],
            conn_type=connection['type'],
            host=connection['host'],
            port=connection['port'],
            schema=connection['schema'],
            login=connection['login'],
            password=connection['password'],
            description=connection['description'],
            extra=json.dumps(connection["extras"]),
            
        )

        session = settings.Session()
        session.add(new_conn)
        session.commit()


def create_variables():
    from airflow.models import Variable
    variables = {
        "demo_custom_operator_3": {
            "source_storage": "devstoreaccount1",
            "source_container": 'source-container',
            "source_file_name": "demo_1.txt",
            "dest_file_name": "demo_100.txt"
        },
        "demo_custom_operator_4": {
            "source_storage": 'devstoreaccount1',
            "source_files": ['demo_1.txt', 'demo_2.txt', 'demo_3.txt', 'demo_4.txt'],
            "source_container": 'source-container',
            "dest_container": 'dest-container' 
        },
        "demo_dynamic_dag_5": {
            "source_storage": 'devstoreaccount1',
            "source_container": 'source-container',
            "dest_container": 'dest-container' 
        }
    }

    _ = [Variable.set(dag, json.dumps(variable)) for dag, variable in variables.items()]



def get_connection():
    session = settings.Session()
    conn = session.query(Connection).filter(Connection.conn_id=="azure_blob").first()

    print("**"*20, conn.host)


# (top-level) DAG & operators
with DAG(dag_id="demo_connections_2",
          default_args=args,
          schedule_interval=None) as dag:

    create_connections = PythonOperator(
        python_callable=create_connections,
        task_id='create_connections'
    )

    create_variables = PythonOperator(
        python_callable=create_variables,
        task_id='create_variables'
    )

    get_connection = PythonOperator(
        python_callable=get_connection,
        task_id='get_connection'
    )

    create_connections >> create_variables >> get_connection

if __name__ == "__main__":
    dag.cli()