import os
import ssl
import uuid
import pandas as pd
from api.logger_config import logger
from db.clickhouse import get_clickhouse_client
from fastapi import HTTPException, Request

client = get_clickhouse_client()

def authenticate(request: Request):
    """
    Authenticate the request using the API key.
    """
    api_key = request.headers.get("x-api-key")
    if api_key is None or api_key not in os.getenv("API_KEYS", "").split(","):
        logger.error("Unauthorized access attempt.")
        raise HTTPException(status_code=401, detail="Unauthorized")

def get_clickhouse_type(pandas_type):
    """
    Map Pandas data types to ClickHouse data types.
    """
    if pd.api.types.is_integer_dtype(pandas_type):
        return 'Int64'
    elif pd.api.types.is_float_dtype(pandas_type):
        return 'Float64'
    elif pd.api.types.is_bool_dtype(pandas_type):
        return 'Bool'
    elif pd.api.types.is_datetime64_any_dtype(pandas_type):
        return 'DateTime'
    else:
        return 'String'

def get_dataset_id():
    """
    Generate a unique dataset ID.
    """
    return str(uuid.uuid4().hex).replace('-', '_')

def get_table_name(dataset_id):
    """
    Generate a table name based on the dataset ID.
    """
    return f"dataset_{dataset_id}"

def parse_date(df):
    """
    Parse the 'Release date' column in the DataFrame.
    """
    try:
        return pd.to_datetime(df['Release date'], errors='coerce', dayfirst=True, format='mixed')
    except Exception as e:
        logger.error(f"Failed to parse 'Release date' column: {e}")
        return None

def process_df(df):
    """
    Process the pandas DataFrame to handle missing values and data types.
    """
    try:
        # Parse the 'Release date' column
        logger.info("Parsing 'Release date' column")
        df['Release date'] = parse_date(df)
        
        # Replace NaN values with None
        df = df.where(pd.notna(df), None)
        
    except Exception as e:
        logger.error(f"Failed to process DataFrame: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to process DataFrame: {e}")
    
    return df

def read_csv_from_url(url):
    """
    Read CSV from a URL and return a pandas DataFrame.
    """
    try:
        # Bypass SSL verification for the CSV URL
        ssl._create_default_https_context = ssl._create_unverified_context
        
        # Read CSV directly from URL
        logger.info(f"Reading CSV from URL: {url}")
        df = pd.read_csv(url)
        
        # Process the DataFrame
        df = process_df(df)
        
        return df
        
    except Exception as e:
        logger.error(f"Failed to parse CSV: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {e}")

def put_in_datasets_metadata(dataset_id, table_name):
    """
    Insert metadata for the dataset into the datasets_metadata table.
    """
    client = get_clickhouse_client()
    insert_metadata_query = f"""
        INSERT INTO datasets_metadata (dataset_id, table_name) VALUES ('{dataset_id}', '{table_name}')
    """
    try:
        logger.info(f"Inserting metadata for dataset: {dataset_id}")
        client.query(insert_metadata_query)
    except Exception as e:
        logger.error(f"Failed to insert metadata for dataset: {dataset_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to insert metadata for dataset: {dataset_id}: {e}")

def parse_date_value(date_str: str) -> str:
    """
    Parse a date string and return it in the 'YYYY-MM-DD' format.
    """
    parsed_date = pd.to_datetime(date_str, errors='coerce', dayfirst=True, format='mixed')
    if pd.isna(parsed_date):
        logger.error(f"Invalid date format: {date_str}")
        raise ValueError(f"Invalid date format: {date_str}")
    return parsed_date.strftime('%Y-%m-%d')

def validate_requested_table(dataset_id):
    """
    Validate the dataset ID and get the table name from the datasets_metadata table.
    """
    if not dataset_id:
        logger.error("dataset_id is required")
        raise HTTPException(status_code=400, detail="dataset_id is required")
    
    client = get_clickhouse_client()
    
    # Validate dataset_id and get table_name from the datasets_metadata table
    dataset_query = f"SELECT table_name FROM datasets_metadata WHERE dataset_id = '{dataset_id}'"
    result = client.query(dataset_query).result_set
    if not result:
        logger.error(f"Invalid dataset_id: {dataset_id}")
        raise HTTPException(status_code=400, detail="Invalid dataset_id")
    table_name = result[0][0]
    
    return table_name

def validate_explore_filters(filters, table_name):
    """
    Validate the filter fields against the table schema.
    """
    client = get_clickhouse_client()
    # Validate filter fields from the database
    fields_query = f"SELECT name FROM system.columns WHERE table = '{table_name}'"
    valid_filter_fields = [row[0] for row in client.query(fields_query).result_set]
    for field in filters.keys():
        if field not in valid_filter_fields:
            logger.error(f"Invalid filter field: {field}")
            raise HTTPException(status_code=400, detail=f"Invalid filter field: {field}")

def get_query_conditions(filters, date_gt, date_lt, table_name):
    """
    Construct query conditions based on filters and date range.
    """
    conditions = []
    if filters:
        validate_explore_filters(filters, table_name)
        for field, value in filters.items():
            if field == "Release date":
                try:
                    parsed_value = parse_date_value(value)
                    conditions.append(f"`{field}` = '{parsed_value}'")
                except ValueError as e:
                    logger.error(f"Failed to parse date in filters: {e}")
                    raise HTTPException(status_code=400, detail=f"Failed to parse date in filters: {e}")
            elif isinstance(value, str):
                conditions.append(f"`{field}` LIKE '%{value}%'")
            else:
                conditions.append(f"`{field}` = {value}")

    # Only add date_gt and date_lt if "Release date" is not in filters
    if "Release date" not in (filters or {}):
        if date_gt:
            parsed_date_gt = parse_date_value(date_gt)
            conditions.append(f"`Release date` > '{parsed_date_gt}'")
        if date_lt:
            parsed_date_lt = parse_date_value(date_lt)
            conditions.append(f"`Release date` < '{parsed_date_lt}'")
    
    return conditions

def construct_query(table_name, filters, date_gt, date_lt, page, page_size):
    """
    Construct the SQL query for exploring data with pagination.
    """
    query = f"SELECT * FROM {table_name}"
    conditions = get_query_conditions(filters, date_gt, date_lt, table_name)
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    total_query = f"SELECT count() FROM ({query})"
    
    # Calculate OFFSET and LIMIT for pagination
    offset = (page - 1) * page_size
    query += f" LIMIT {page_size} OFFSET {offset}"
    
    logger.info(f"Constructed query: {query}")
    logger.info(f"Constructed total query: {total_query}")
    
    return query, total_query