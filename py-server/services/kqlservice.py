import json
from azure.kusto.data import KustoClient, KustoConnectionStringBuilder


def execute_query(cluster: str, database: str, query: str) -> str:
    """
    Executes a KQL query against the specified Azure Data Explorer cluster and database.

    :param cluster: The name of the Azure Data Explorer cluster.
    :param database: The name of the database to query.
    :param query: The KQL query to execute.
    :return: The result of the query as a JSON string.
    """
    try:
        # Authenticate using Azure CLI (you can also use AAD app or device code)
        cluster = f"https://{cluster}.kusto.windows.net"
        kcsb = KustoConnectionStringBuilder.with_az_cli_authentication(cluster)

        # Create Kusto client
        client = KustoClient(kcsb)

        # Execute query
        response = client.execute(database, query)

        # Convert response to JSON format
        results = response.primary_results[0]

        # Convert results to a list of dictionaries
        rows = []
        columns = [col.column_name for col in results.columns]

        for row in results:
            row_dict = {}
            for i, col in enumerate(columns):
                row_dict[col] = row[i]
                rows.append(row_dict)

        results = rows

        return json.dumps(results, indent=2)
    except Exception as e:
        return "Unable to execute query: " + str(e)


def get_schema(cluster: str, database: str, table: str) -> str:

    try:
        # Authenticate using Azure CLI (you can also use AAD app or device code)
        cluster = f"https://{cluster}.kusto.windows.net"
        kcsb = KustoConnectionStringBuilder.with_az_cli_authentication(cluster)

        # Create Kusto client
        client = KustoClient(kcsb)

        # Query to get table schema
        query = f"{table} | getschema"

        # Execute query
        response = client.execute(database, query)

        # Print schema
        # Create a dictionary of column names and types
        schema_dict = {}
        for row in response.primary_results[0]:
            schema_dict[row["ColumnName"]] = row["ColumnType"]

        # Return the schema dictionary
        return json.dumps(schema_dict, indent=2)
    except Exception as e:
        return "Unable to get schema: " + str(e)
