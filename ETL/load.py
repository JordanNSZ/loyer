from google.cloud import bigquery
from google.cloud.exceptions import NotFound


client = bigquery.Client()

project_id = "loyer-43000"
dataset_id = "loyer"
table_id = "loyer-lyon"

# Créer la base de données (DB).
def db_creation(project_id=project_id, dataset_id=dataset_id, table_id=table_id):
    dataset_ref = bigquery.DatasetReference(project_id, dataset_id)
    
    try:
        client.get_dataset(dataset_ref)
        print(f"Dataset {dataset_id} already exists.")
    except NotFound:
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "europe-west1"  
        dataset = client.create_dataset(dataset)
        print(f"Created dataset {dataset_id}.")

# Créer la table loyer-lyon.
def table_creation(project_id=project_id, dataset_id=dataset_id, table_id=table_id):
    dataset_ref = bigquery.DatasetReference(project_id, dataset_id)
    table_ref = dataset_ref.table(table_id)

    try:
        client.get_table(table_ref)
        print(f"Table {table_id} already exists.")
    except NotFound:

        schema = [
            bigquery.SchemaField("id", "INTEGER"),
            bigquery.SchemaField("housing_type", "STRING"),
            bigquery.SchemaField("price", "FLOAT64"),
            bigquery.SchemaField("nbr_rooms", "INTEGER"), #INTEGER or SMALLINT are aliases for INT64
            bigquery.SchemaField("area", "FLOAT64"),
            bigquery.SchemaField("location", "STRING"),
        ]

        table = bigquery.Table(table_ref, schema=schema)
        table = client.create_table(table)
        print(f"Created table {table_id}.")

# Charger les données.
def data_loading(file_path = "data/loyer_lyon.csv"):
    source_format = bigquery.SourceFormat.CSV #.parquet
    job_config = bigquery.LoadJobConfig(
        source_format=source_format,
        skip_leading_rows=1,
        #autodetect=True, #the schema has been specified.
    )

    with open(file_path, "rb") as source_file:
        load_job = client.load_table_from_file(source_file, table_ref, job_config=job_config)

    load_job.result()

    print(f"Loaded {load_job.output_rows} rows into {dataset_id}:{table_id}.")

import extract
import transform

def main():
    get_pages(start=1, stop=3)
    pages_parser()
    #ajouter un worflow pour commit-push la base de données enregistré dans le repertoire courant sous
    #loyer_lyon.csv
    db_creation()
    table_creation()
    data_loading()
    
if __name__ == "__main__":
    main()
