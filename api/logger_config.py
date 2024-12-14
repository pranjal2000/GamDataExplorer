import logging

def setup_logging():
    logging.basicConfig(
        level=logging.DEBUG,  # Capture all log levels
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

setup_logging()
logger = logging.getLogger(__name__)