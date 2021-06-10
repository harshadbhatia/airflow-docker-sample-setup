from airflow.hooks.base_hook import BaseHook

from datetime import datetime, timedelta

from azure.storage.blob import (
    BlobServiceClient,
    ContainerClient,
    AccountSasPermissions,
    ResourceTypes,
    generate_account_sas
)



class AzureBlobServiceHook(BaseHook):
    def __init__(
            self,
            conn_id,
            storage_name,
            container_name,
            *args,
            **kwargs
    ):
        """
        """

        self.ab = None
        self.conn_id = conn_id
        self.storage_name = storage_name
        self.container_name = container_name
        self._args = args
        self._kwargs = kwargs

        # get the connection parameters
        self.connection = self.get_connection(self.conn_id)
        self.extras = self.connection.extra_dejson

    
    def get_blob_endpoint(self):
        return f"http://{self.connection.host}:{self.connection.port}/{self.storage_name}"
    
    def get_token(self):
        return self.connection.password

    def create_conn_string(self):
        conn_string = f"""DefaultEndpointsProtocol={self.extras["extra__wasb__DefaultEndpointsProtocol"]}
        AccountName={self.storage_name}
        AccountKey={self.connection.password}
        BlobEndpoint={self.get_blob_endpoint()}
        """.replace("\n", ";").replace(" ", "")

        return conn_string
    
    def create_blob_service(self):
        return BlobServiceClient(account_name=self.connection.storage_name, account_key=self.connection.password)
        
    def create_blob_container_client(self):
        return ContainerClient.from_connection_string(self.create_conn_string(), self.container_name)

    def create_sas_token(self):
        return generate_account_sas(
            account_name=self.storage_name,
            account_key=self.connection.password,
            resource_types=ResourceTypes(service=True, container=True, object=True),
            permission=AccountSasPermissions(read=True, write=True, add=True, create=True),
            expiry=datetime.utcnow() + timedelta(hours=1)
        )

    def get_conn(self):
    
        if self.ab:
            return self.ab
        
        self.ab = self.create_blob_container_client()

        return self.ab