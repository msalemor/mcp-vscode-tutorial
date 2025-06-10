import json
from azure.kusto.data import KustoClient, KustoConnectionStringBuilder

def get_schema(cluster: str, database: str, table:str) -> str:


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
        schema_dict[row['ColumnName']] = row['ColumnType']
    
    # Return the schema dictionary
    return json.dumps(schema_dict, indent=2)
