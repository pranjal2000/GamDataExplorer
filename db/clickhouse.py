import os
import clickhouse_connect
from api.logger_config import logger
from clickhouse_driver.errors import Error

class ClickHouseClientSingleton:
    """
    Singleton class to ensure only one instance of the ClickHouse client is created.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ClickHouseClientSingleton, cls).__new__(cls)
            cls._instance._client = None
        return cls._instance

    def get_client(self):
        """
        Get the ClickHouse client instance. If it doesn't exist, create a new one.
        """
        if self._client is None:
            CLICKHOUSE_HOST = os.getenv("CLICKHOUSE_HOST")
            CLICKHOUSE_PORT = os.getenv("CLICKHOUSE_PORT")
            CLICKHOUSE_USER = os.getenv("CLICKHOUSE_USER")
            CLICKHOUSE_PASSWORD = os.getenv("CLICKHOUSE_PASSWORD")

            # Check if required environment variables are set
            if not CLICKHOUSE_HOST or not CLICKHOUSE_PORT or not CLICKHOUSE_USER:
                logger.error("Missing required environment variables for ClickHouse connection")
                raise ValueError("Missing required environment variables for ClickHouse connection")
            
            try:
                # Create a new ClickHouse client
                self._client = clickhouse_connect.get_client(
                    host=CLICKHOUSE_HOST,
                    port=int(CLICKHOUSE_PORT),
                    user=CLICKHOUSE_USER,
                    password=CLICKHOUSE_PASSWORD,
                    secure=True,
                    verify=False
                )
                # Log a successful connection
                logger.info("DB Ping: " + str(self._client.query("SELECT 1").result_set[0][0]))
            except Error as e:
                logger.error(f"Failed to connect to ClickHouse: {e}")
                raise
        return self._client

def get_clickhouse_client():
    """
    Get the ClickHouse client instance.
    """
    return ClickHouseClientSingleton().get_client()