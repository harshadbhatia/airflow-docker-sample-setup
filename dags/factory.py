from pathlib import Path

from airflow import DAG
import dagfactory

dag_factory = dagfactory.DagFactory(f"{Path(__file__).parent.absolute()}/factory.yml")

dag_factory.clean_dags(globals())
dag_factory.generate_dags(globals())