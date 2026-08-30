"""
ETL Tools
=========
Provides core Extract, Transform, and Load (ETL) operations used by
the ETL Analyst agent for data pipeline tasks.

Operations:
    - extract_load: Fetch data from REST APIs and save to files
    - transform_load_context: Read files and return sample data for LLM context
    - execute_code: Dynamically execute generated pandas code
"""

import os
import re
import requests
import pandas as pd


class ETLTools:
    """
    Utility class providing ETL operations for the data agent.

    Handles data extraction from APIs, file reading for context,
    and dynamic code execution for data transformations.

    Example:
        >>> tools = ETLTools()
        >>> tools.extract_load("https://pokeapi.co/api/v2/pokemon/", "data/extract", "csv")
        >>> context = tools.transform_load_context("data/extract/extracted_data.csv")
    """

    def __init__(self):
        """Initialize ETLTools (no configuration required)."""
        pass

    def extract_load(self, url: str, output_folder: str, format: str) -> str:
        """
        Extract data from a REST API endpoint and save to a local file.

        Fetches JSON data from the given URL, normalizes nested structures
        using pandas, and saves the result in the specified format.

        Args:
            url (str): The API endpoint URL to fetch data from.
            output_folder (str): Relative path to the output directory
                                 (resolved from project root).
            format (str): Output file format. Supported: "csv", "json", "parquet".

        Returns:
            str: Success message with file path, or error message on failure.

        Example:
            >>> tools = ETLTools()
            >>> tools.extract_load("https://pokeapi.co/api/v2/pokemon/", "data/extract", "csv")
        """
        # Resolve output path relative to project root
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        output_folder = os.path.join(project_root, output_folder)
        os.makedirs(output_folder, exist_ok=True)

        try:
            # Fetch data from API
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()

            # Normalize nested JSON and save in requested format
            filename = os.path.join(output_folder, f"extracted_data.{format}")
            df = pd.json_normalize(data["results"])

            if format == "csv":
                df.to_csv(filename, index=False)
            elif format == "json":
                df.to_json(filename, orient="records", lines=True)
            elif format == "parquet":
                df.to_parquet(filename, index=False)
            else:
                return f"Unsupported format: {format}. Use csv, json, or parquet."

            return f"Data successfully extracted and saved to {filename}"

        except requests.exceptions.RequestException as e:
            return f"Failed to extract data: {e}"

    def transform_load_context(self, file_path: str) -> str:
        """
        Read a data file and return sample rows for LLM context.

        This method provides the LLM with a preview of the data structure
        so it can generate appropriate transformation code.

        Args:
            file_path (str): Path to the input data file.

        Returns:
            str: String representation of the first 3 rows, or error message.
        """
        file_extension = os.path.splitext(file_path)[1].lower()

        try:
            if file_extension == ".csv":
                df = pd.read_csv(file_path)
            elif file_extension == ".json":
                df = pd.read_json(file_path, lines=True)
            elif file_extension == ".parquet":
                df = pd.read_parquet(file_path)
            else:
                return f"Unsupported file format: {file_extension}"

            return str(df.head(3))

        except Exception as e:
            return f"Error reading file: {e}"

    def execute_code(self, code: str) -> str:
        """
        Execute dynamically generated pandas code.

        This method is used by the ETL agent to run LLM-generated
        transformation code. The code typically reads a file, transforms
        the data, and saves the result.

        ⚠️ Security Note: Uses exec() for dynamic code execution.
           This is intended for development/prototyping only.
           In production, use a sandboxed execution environment.

        Args:
            code (str): Python code string to execute.

        Returns:
            str: Success message or error details if execution fails.
        """
        try:
            exec(code)
            return "Code executed successfully"
        except Exception as e:
            return f"Failed to execute code: {e}"


if __name__ == "__main__":
    # Quick test: extract Pokemon data from PokeAPI
    tools = ETLTools()
    result = tools.extract_load(
        "https://pokeapi.co/api/v2/pokemon/",
        "data/extract",
        "csv",
    )
    print(result)
