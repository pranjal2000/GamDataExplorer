# GameDataExplorer

## Overview

GameDataExplorer is a FastAPI-based application that allows users to upload CSV files and explore the data stored in a ClickHouse database. The application provides endpoints to upload CSV files from a URL and query the data using various filters.

App deployed here - https://data-explorer-eta.vercel.app/

## Features

- Upload CSV files from a URL and store the data in ClickHouse.
- Query the data using various filters.

## API Documentation

### Upload CSV

**Endpoint**: `/upload_csv`

**Method**: `POST`

**Request Body**:
```json
{
    "csv_url": "string"
}
```

**Response**:
```json
{
    "status": "success",
    "dataset_id": "string"
}
```

### Explore Data

**Endpoint**: `/explore`

**Method**: `GET`

**Query Parameters**:
- `field`: The field to query.
- `value`: The value to query.

**Response**:
```json
{
    "data": [
        {
            "Name": "Galac",
            "Release Date": "October 21, 2008",
            ...
        }
    ]
}
```

## Setup Instructions

### Prerequisites

- Python 3.9 or higher
- Docker
- Docker Compose

### Local Setup

1. Clone the repository:
    ```sh
    git clone https://github.com/your-username/GameDataExplorer.git
    cd GameDataExplorer
    ```

2. Create and activate a virtual environment:
    ```sh
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```

4. Set up environment variables:
    - Create a `.env` file in the root directory and add the following environment variables:
        ```env
        CLICKHOUSE_HOST=clickhouse
        CLICKHOUSE_PORT=9000
        CLICKHOUSE_USER=default
        CLICKHOUSE_PASSWORD=
        API_KEYS=your_api_key_1,your_api_key_2
        ```

5. Run the database initialization script:
    ```sh
    python db/init_db.py
    ```

6. Run the FastAPI application:
    ```sh
    uvicorn api.main:app --host 0.0.0.0 --port 8000
    ```

7. Local Frontend Setup
    - Serve the frontend using a simple HTTP server:

    - If you have Python installed, you can use the built-in HTTP server to serve the frontend.

    ```sh
    cd GameDataExplorer
    python -m http.server 8001  
    ```

### Docker Setup

1. Build and run the Docker containers:
    ```sh
    docker-compose -f docker/docker-compose.yml up --build
    ```

2. Access the application:
    - Open your web browser and navigate to `http://localhost:8001` to access the frontend.

