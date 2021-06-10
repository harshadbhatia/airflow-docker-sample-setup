from tempfile import NamedTemporaryFile

import os
import logging
import json
import uuid
import subprocess
import concurrent

from airflow.utils.decorators import apply_defaults
from airflow.models import BaseOperator

from azureP.hooks.azure_blob_hook import AzureBlobServiceHook


class AzureAZCopyOperator(BaseOperator):
    """
    """

    def __init__(self,
                 azure_source_conn_id,
                 azure_dest_conn_id,
                 source_storage,
                 source_container,
                 
                 dest_container,

                 source_file_name=None,
                 dest_file_name=None,
                 source_files=None,

                 *args,
                 **kwargs):

        super().__init__(*args, **kwargs)

        self.azure_source_conn_id = azure_source_conn_id
        self.azure_dest_conn_id = azure_dest_conn_id

        self.source_storage = source_storage
        self.source_container = source_container
        self.source_file_name = source_file_name
        
        self.dest_container = dest_container
        self.dest_file_name = dest_file_name
        self.source_files = source_files
    
    def execute_command(self, command):
        return subprocess.run(command, shell=True, check=True, capture_output=True)
     

    def copy_file(self, source, dest):
        # Pending defect with AZCopy where source is unkown
        uid = uuid.uuid4()
        self.execute_command(f"azcopy copy '{source}' '/tmp/{uid}' --from-to BlobLocal")
        self.execute_command(f"azcopy copy '/tmp/{uid}' '{dest}' --from-to LocalBlob")
    
    def get_url(self, endpoint, container, file_name, key):
        return f"{endpoint}/{container}/{file_name}?{key}"

    def execute(self, context):

        logging.info("Starting threadpool for AZCopy")

        hook = AzureBlobServiceHook(
            conn_id=self.azure_source_conn_id, 
            storage_name=self.source_storage,
            container_name=self.source_container
        )

        token = hook.create_sas_token()
        files = self.source_files if self.source_files else [self.source_file_name]
        
        # Source: Destination
        source_dest = {
            self.get_url(hook.get_blob_endpoint(), self.source_container, file, token): 
            self.get_url(hook.get_blob_endpoint(), self.dest_container, file, token)
            for file in files
        }

        # Make it little more threads shall we ?
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            
            futures =[executor.submit(self.copy_file, source, dest) for source, dest in source_dest.items()]
            
            for future in concurrent.futures.as_completed(futures):
                try:
                    logging.info(future.result())
                except Exception as e:
                    logging.error(f"{e}")

        

