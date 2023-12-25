from datetime import datetime
from airflow.decorators import dag, task
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateEmptyDatasetOperator

from astro import sql as aql
from astro.files import File
from astro.sql.table import Table, Metadata
from astro.constants import FileType



#setting general set-up

@dag(
    start_date=datetime(2023,1,1),
    schedule=None,
    catchup=False,
    tags=['covid']
)

def covid():
    upload_csv_to_gcs = LocalFilesystemToGCSOperator(
        task_id='upload_csv_to_gcs',
        src='include/dataset/covid19.csv',
        dst= 'raw/covid19.csv',
        bucket='airflow-learn-bucket',
        gcp_conn_id='gcp',
        mime_type='text/csv'
    )

    create_table_bq = BigQueryCreateEmptyDatasetOperator(
        task_id = 'create_table_bq',
        dataset_id= 'covid',
        gcp_conn_id='gcp'
    )

    gcs_to_bq = aql.load_file(
        task_id='gcs_to_bq',
        input_file=File(
            'gs://airflow-learn-bucket/raw/covid19.csv',
            conn_id='gcp',
            filetype=FileType.CSV
        ),
        output_table=Table(
            name = 'raw_covid',
            conn_id= 'gcp',
            metadata=Metadata(schema='covid')
        ),
        use_native_support=True

    )


covid()