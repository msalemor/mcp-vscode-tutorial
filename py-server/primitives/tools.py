import json
import mcp.types as types

from mcp.server.lowlevel import Server
from services.configloader import ConfigLoader, SchemaData
from services.kqlservice import get_schema as kql_get_schema,execute_query
from services.webservices import fetch_website

loader = ConfigLoader()

async def get_kql_schema(name: str) -> list[types.TextContent]:
    table : SchemaData= loader.get_by_type_key("schema",name)
    if table:
        # Extract the table name from schemaCmd (e.g., 'Employees | getschema' -> 'Employees')
        table_name = table.data.schemaCmd.split(' ')[0]
        schema = kql_get_schema(table.data.cluster, table.data.database, table_name)
        resp = {"cluster": table.data.cluster,
                "database": table.data.database,
                "table": table_name,
                "schema": schema,
                "description": table.data.description}

        return [types.TextContent(type="text", text=json.dumps(resp, indent=2))]
    raise ValueError(f"Unknown schema: {name}")

def configure_tools(app:Server)-> None:
    @app.call_tool()
    async def server_tools(
        name: str, arguments: dict
    ) -> list[
        types.TextContent
        | types.ImageContent        
        | types.EmbeddedResource
    ]:
        match name:
            case "fetch":
                if name != "fetch":
                    raise ValueError(f"Unknown tool: {name}")
                if "url" not in arguments:
                    raise ValueError("Missing required argument 'url'")
                return await fetch_website(arguments["url"])
            case "schema":
                if name != "schema":
                    raise ValueError(f"Unknown tool: {name}")
                if "tableName" not in arguments:
                    raise ValueError("Missing required argument 'tableName'")
                return await get_kql_schema(arguments["tableName"])
            case "querykql":
                if name != "querykql":
                    raise ValueError(f"Unknown tool: {name}")
                if not all(k in arguments for k in ["queryName", "parameter"]):
                    raise ValueError("Missing required arguments 'queryName' or 'parameter'")
                if arguments["queryName"] == "employeeroles":
                    qinfo = loader.get_by_type_key("query", arguments["queryName"])
                    cluster = qinfo.data.cluster
                    database = qinfo.data.database
                    query = qinfo.data.queryCmd.replace("<parameter>", arguments["parameter"])
                    return [types.TextContent(type="text", text=execute_query(cluster,database,query))]
                raise ValueError(f"Unknown query name: {arguments['queryName']}")
            case "math":             
                if not all(k in arguments for k in ["a", "b", "operation"]):
                    raise ValueError("Missing required arguments 'a', 'b', or 'operation'")

                a = arguments["a"]
                b = arguments["b"]
                operation = arguments["operation"]
                
                if operation == "add":
                    result = a + b
                elif operation == "subtract":
                    result = a - b
                elif operation == "multiply":
                    result = a * b
                elif operation == "divide":
                    if b == 0:
                        raise ValueError("Division by zero is not allowed")
                    result = a / b
                else:
                    raise ValueError(f"Unknown operation: {operation}")
                return [types.TextContent(type="text", text=str(result))]
            case _:
                raise ValueError(f"Unknown tool: {name}")
               
    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        return [
            types.Tool(
                name="fetch",
                description="Fetches a website and returns its content",
                inputSchema={
                    "type": "object",
                    "required": ["url"],
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "URL to fetch",
                        }
                    },
                },
            ),
            types.Tool(
                name="schema",
                description="fetches a schema for a given table name",
                inputSchema={
                    "type": "object",
                    "required": ["tableName"],
                    "properties": {
                        "tableName": {
                            "type": "string",
                            "description": "Table name to fetch schema for",
                        }
                    },
                },
            ),
            types.Tool(
                name="querykql",
                description="Gets data by executing a KQL query",
                inputSchema={
                    "type": "object",
                    "required": ["queryName","parameter"],
                    "properties": {
                        "queryName": {
                            "type": "string",
                            "description": "The name of the query to execute",
                        },
                        "parameter": {
                            "type": "string",
                            "description": "The parameter to use in the query",
                        }
                    },
                },
            ),
            types.Tool(
                name="math",
                description="Adds, subtracts, multiplies, or divides two numbers",
                inputSchema={
                    "type": "object",
                    "required": ["a","b","operation"],
                    "properties": {
                        "a": {
                            "type": "number",
                            "description": "first number",
                        },
                        "b": {
                            "type": "number",
                            "description": "second number",
                        },
                        "operation": {
                            "type": "string",
                            "enum": ["add", "subtract", "multiply", "divide"],
                            "description": "Operation to perform",
                        }
                    },
                },
            )
        ]
    