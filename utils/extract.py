import jaydebeapi
import logging
from pathlib import Path
from typing import List, Tuple, Dict, Union, Any


def connect_to_db(job_config: Dict[str, Any]) -> jaydebeapi.Connection:
    """
    Connects to the database using the provided job configuration.

    Args:
        job_config: The nested job configuration dictionary.

    Returns:
        The database connection object.

    Raises:
        ValueError: If required keys are missing from the config.
        Exception: If the database connection fails.
    """
    source_config = job_config["source"]
    required_keys = ["user", "password", "conn_string", "driver_name", "driver_file"]
    if not all(source_config.get(key) for key in required_keys):
        missing_keys = [key for key in required_keys if not source_config.get(key)]
        raise ValueError(f"Missing required source config keys: {missing_keys}")

    try:
        return jaydebeapi.connect(
            source_config.get("driver_name"),
            source_config.get("conn_string"),
            [source_config.get("user"), source_config.get("password")],
            source_config.get("driver_file"),
        )
    except Exception as e:
        logging.exception(f"Failed to connect to database: {e}")
        raise


def load_query(query_file_path: Union[str, Path]) -> str:
    """
    Loads the SQL query from the specified file.

    Args:
        query_file_path: The path to the SQL query file (str or Path).

    Returns:
        The SQL query as a string.

    Raises:
        FileNotFoundError: If the query file doesn't exist.
        Exception: For other errors during file reading.
    """
    try:
        with open(query_file_path, "r") as f:
            query = f.read()
        return query
    except FileNotFoundError:
        logging.exception(f"Query file not found: {query_file_path}")
        raise
    except Exception as e:
        logging.exception(f"Failed to load query from file: {query_file_path}")
        raise


def query_db(
    db_connection: jaydebeapi.Connection, query: str
) -> Tuple[List[str], List[Tuple[Any, ...]]]:
    """
    Executes the SQL query on the database connection.

    Args:
        db_connection: The database connection object.
        query: The SQL query to execute.

    Returns:
        A tuple: (headers, data).  `headers` is a list of column names (strings).
                 `data` is a list of tuples, where each tuple represents a row.

    Raises:
        Exception: If any error occurs during query execution.
    """
    try:
        with db_connection.cursor() as cursor:
            cursor.execute(query)
            header = [col[0] for col in cursor.description]
            data = cursor.fetchall()
        return header, data
    except Exception as e:
        logging.exception(f"Failed to execute database query: {e}")
        raise


def extract_data(
    job_config: Dict[str, Any], query_file_path: Union[str, Path]
) -> Tuple[List[str], List[Tuple[Any, ...]]]:
    """
    Extracts data from the database specified in the job configuration.

    Args:
        job_config: The nested job configuration dictionary.
        query_file_path: The path to the SQL query file (str or Path).

    Returns:
        A tuple: (headers, data).  `headers` is a list of column names (strings).
                 `data` is a list of tuples, where each tuple represents a row.

    Raises:
        Exception: If any error occurs during extraction.
    """
    try:
        with connect_to_db(job_config) as db_connection:
            logging.info(
                f"Connected to {job_config['source']['source_name']} database."
            )
            query = load_query(query_file_path)
            header, data = query_db(db_connection, query)
            logging.info(f"Data retrieved from database")
        return header, data

    except Exception as e:
        logging.exception(f"An error occurred during data extraction: {e}")
        raise
