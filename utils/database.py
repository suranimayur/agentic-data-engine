"""
Database Utility
================
Provides a wrapper around psycopg2 for PostgreSQL operations including
schema introspection and SQL query execution.

This module is used by the SQL Analyst agent to:
1. Fetch database schema details (tables, columns, types, sample data)
   for injecting into LLM prompts as context.
2. Execute generated SQL queries safely.
"""

import psycopg2


class DatabaseUtil:
    """
    PostgreSQL database utility for schema introspection and query execution.

    Establishes a connection to PostgreSQL on initialization and provides
    methods to retrieve schema information and execute SQL queries.

    Attributes:
        db_config (dict): PostgreSQL connection configuration.
        connection: Active psycopg2 connection object.

    Example:
        >>> config = {"host": "localhost", "port": 5432, "database": "mydb",
        ...           "user": "admin", "password": "secret"}
        >>> db = DatabaseUtil(config)
        >>> schema = db.schema_details("public")
        >>> result = db.execute_sql("SELECT COUNT(*) FROM users")
    """

    def __init__(self, db_config: dict):
        """
        Initialize DatabaseUtil and establish a PostgreSQL connection.

        Args:
            db_config (dict): Connection parameters containing:
                - host (str): Database host
                - port (int): Database port
                - database (str): Database name
                - user (str): Database user
                - password (str): Database password
        """
        self.db_config = db_config
        self.connection = None

        try:
            self.connection = psycopg2.connect(**db_config)
        except Exception as e:
            print(f"Error connecting to the database: {e}")

    def schema_details(self, schema_name: str) -> str:
        """
        Fetch complete schema information for a PostgreSQL schema.

        Retrieves table names, column definitions (name + data type),
        and 5 sample rows per table. This information is used as
        context in LLM prompts for SQL query generation.

        Args:
            schema_name (str): The PostgreSQL schema name (typically "public").

        Returns:
            str: A formatted string containing the full schema details,
                 or an error message if the operation fails.

        Raises:
            ConnectionError: If the database connection is not available.
        """
        if self.connection is None:
            raise ConnectionError(
                "Database connection failed. Cannot fetch schema details."
            )

        cursor = self.connection.cursor()
        schema_info = f"Database Schema: {schema_name}\n"

        try:
            # Step 1: Get all tables in the schema
            cursor.execute(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = %s;",
                (schema_name,),
            )
            tables_list = cursor.fetchall()

            for table in tables_list:
                table_name = table[0]
                schema_info += f"\nTable: {table_name}\n"

                # Step 2: Get columns and data types for this table
                cursor.execute(
                    "SELECT column_name, data_type "
                    "FROM information_schema.columns "
                    "WHERE table_name = %s;",
                    (table_name,),
                )
                for column in cursor.fetchall():
                    schema_info += f"  Column: {column[0]}, Data Type: {column[1]}\n"

                # Step 3: Fetch 5 sample rows for LLM context
                cursor.execute(
                    f"SELECT * FROM {schema_name}.{table_name} LIMIT 5;"
                )
                schema_info += "  Sample Data:\n"
                for row in cursor.fetchall():
                    schema_info += f"    {row}\n"

        except Exception as e:
            print(f"Error fetching schema details: {e}")
            schema_info = f"Error fetching schema details: {e}"

        finally:
            cursor.close()
            self.connection.close()

        return schema_info

    def execute_sql(self, query: str) -> str:
        """
        Execute a SQL query and return the results as a string.

        This method is called after the SQL safety judge has validated
        that the query is safe (SELECT-only, no manipulation commands).

        Args:
            query (str): The SQL query to execute.

        Returns:
            str: Query results as a string, or an error message if execution fails.

        Raises:
            ConnectionError: If the database connection is not available.
            ValueError: If the query is empty.
        """
        cursor = None
        try:
            if self.connection is None:
                raise ConnectionError(
                    "Database connection failed. Cannot execute query."
                )

            query = (query or "").strip()
            if not query:
                raise ValueError("Query is empty. Cannot execute.")

            cursor = self.connection.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
            self.connection.commit()
            return str(result)

        except Exception as e:
            print(f"Error executing query: {e}")
            return f"Error executing query: {e}"

        finally:
            if cursor:
                cursor.close()
            if self.connection:
                self.connection.close()
