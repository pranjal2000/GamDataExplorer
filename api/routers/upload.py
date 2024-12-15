import pandas as pd
from fastapi import APIRouter, Depends, HTTPException

from api.logger_config import logger
from db.clickhouse import get_clickhouse_client
from api.utils import authenticate, read_csv_from_url, get_dataset_id, get_table_name, get_clickhouse_type, put_in_datasets_metadata

from api.schemas import CSVUploadRequest, CSVUploadResponse

router = APIRouter()

@router.post("/upload_csv", response_model=CSVUploadResponse, dependencies=[Depends(authenticate)])
def upload_csv(request: CSVUploadRequest):
    """
        Upload a CSV file from a URL and store its data in ClickHouse.

        Args:
            request (CSVUploadRequest): The request body containing the CSV URL.
        
        Headers:
            x-api-key (str): The API key for authentication.
            Content-Type (str): application/json

        Returns:
            CSVUploadResponse: The response containing the status and dataset ID.

        Raises:
            HTTPException: If there is an error reading the CSV or storing the data.
    """   
    # Read CSV from URL
    df = read_csv_from_url(str(request.csv_url))
    
    return store_df_in_clickhouse(df)

def store_df_in_clickhouse(df: pd.DataFrame):
    # Generate unique dataset ID and table name
    dataset_id = get_dataset_id()
    table_name = get_table_name(dataset_id)
    put_in_datasets_metadata(dataset_id, table_name)
    
    client = get_clickhouse_client()
    
    # Create table query with explicit schema
    create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            {', '.join([f'`{col}` {get_clickhouse_type(df[col].dtype)}' if df[col].notna().all() else f'`{col}` Nullable({get_clickhouse_type(df[col].dtype)})' for col in df.columns])}
        )
        ENGINE = MergeTree()
        PARTITION BY `Release date`
        ORDER BY AppID
    """
    
    try:
        # Execute create table query
        logger.info(f"Creating table: {table_name}")
        client.query(create_table_query)
        
        # Insert data from pandas DataFrame into ClickHouse table
        logger.info(f"Inserting data into table: {table_name}")
        client.insert_df(table_name, df)
    except Exception as e:
        logger.error(f"Failed to store CSV data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to store CSV data: {e}")

    logger.info(f"Successfully stored CSV data in table: {table_name}")
    return {"status": "success", "dataset_id": dataset_id, "table_name": table_name}
