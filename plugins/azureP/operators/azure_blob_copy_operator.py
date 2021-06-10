import logging
import json

from airflow.utils.decorators import apply_defaults
from airflow.models import BaseOperator

from azureP.hooks.azure_blob_hook import AzureBlobServiceHook


class AzureBlobCopyOperator(BaseOperator):
    """
    """

    def __init__(self,
                 azure_source_conn_id,
                 azure_dest_conn_id,
                 source_storage,
                 source_container,
                 source_file_name,

                 dest_file_name,
                 *args,
                 **kwargs):

        super().__init__(*args, **kwargs)

        self.azure_source_conn_id = azure_source_conn_id
        self.azure_dest_conn_id = azure_dest_conn_id

        self.source_storage = source_storage
        self.source_container = source_container
        self.source_file_name = source_file_name
        
        self.dest_file_name = dest_file_name
    

    def execute(self, context):

        logging.info("Starting our new custom operator")
        ab_source_hook = AzureBlobServiceHook(
            conn_id=self.azure_source_conn_id, 
            storage_name=self.source_storage,
            container_name=self.source_container
        )

        source_blob_url = f"{ab_source_hook.get_blob_endpoint()}/{self.source_container}/{self.source_file_name}"

        logging.info("Initiating Copy Bob")
        copied_blob = ab_source_hook.get_conn().get_blob_client(blob=self.dest_file_name)
        
        logging.info(f"Starting Copy from - {source_blob_url}")
        copy = copied_blob.start_copy_from_url(source_blob_url)

        props = copied_blob.get_blob_properties()
        logging.info(f"Copy Status = {props.copy.status}")

