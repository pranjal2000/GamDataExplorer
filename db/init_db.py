import sys
sys.path.append('../')
from dotenv import load_dotenv
from db.clickhouse import get_clickhouse_client

from api.logger_config import logger

def init_db():
    client = get_clickhouse_client()
    # Create a table for storing datasets metadata
    create_metadata_table_query = """
    CREATE TABLE IF NOT EXISTS datasets_metadata (
        dataset_id String,
        table_name String,
        upload_time DateTime DEFAULT now()
    ) ENGINE = MergeTree() ORDER BY dataset_id
    """
    try:
        client.query(create_metadata_table_query)
        logger.info("Successfully created datasets_metadata table")
    except Exception as e:
        logger.error(f"Failed to create datasets_metadata table: {e}")
        raise

if __name__ == "__main__":
    load_dotenv()
    init_db()