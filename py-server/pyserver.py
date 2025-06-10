import sys
import anyio
import click
import json
import mcp.types as types
from mcp.server.lowlevel import Server
from pydantic import AnyUrl

from services.kqlservice import get_schema as kql_get_schema
from services.configloader import SchemaConfigLoader, SchemaConfig, SchemaConfigsSingleton
from services.webservices import fetch_website

schema_loader = SchemaConfigsSingleton.get_instance()
# table = config.get_configs_by_name("employees")
# if table:
#     schema = kql_get_schema(table.cluster, table.database, table.table)


SAMPLE_RESOURCES = {
    "greeting": "Hello! This is a sample text resource.",
    "help": "This server provides a few sample text resources for testing.",
    "about": "This is the simple-resource MCP server implementation.",
}

def create_messages(
    context: str | None = None, topic: str | None = None
) -> list[types.PromptMessage]:
    """Create the messages for the prompt."""
    messages = []

    # Add context if provided
    if context:
        messages.append(
            types.PromptMessage(
                role="user",
                content=types.TextContent(
                    type="text", text=f"Here is some relevant context: {context}"
                ),
            )
        )

    # Add the main prompt
    prompt = "Please help me with "
    if topic:
        prompt += f"the following topic: {topic}"
    else:
        prompt += "whatever questions I may have."

    messages.append(
        types.PromptMessage(
            role="user", content=types.TextContent(type="text", text=prompt)
        )
    )

    return messages

async def get_kql_schema(name: str) -> list[types.TextContent]:
    table = schema_loader.get_configs_by_name(name)
    if table:
        schema = kql_get_schema(table.cluster, table.database, table.table)
        resp = {"cluster": table.cluster,
                "database": table.database,
                "table": table.table,
                "schema": schema,
                "description": table.description}

        return [types.TextContent(type="text", text=json.dumps(resp, indent=2))]
    raise ValueError(f"Unknown schema: {name}")


@click.command()
@click.option("--port", default=8000, help="Port to listen on for SSE")
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="stdio",
    help="Transport type",
)
def main(port: int, transport: str) -> int:
    app = Server("mcp-server")

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

    @app.list_prompts()
    async def list_prompts() -> list[types.Prompt]:
        return [
            types.Prompt(
                name="simple",
                description="A simple prompt that can take optional context and topic "
                "arguments",
                arguments=[
                    types.PromptArgument(
                        name="context",
                        description="Additional context to consider",
                        required=False,
                    ),
                    types.PromptArgument(
                        name="topic",
                        description="Specific topic to focus on",
                        required=False,
                    ),
                ],
            )
        ]

    @app.get_prompt()
    async def get_prompt(
        name: str, arguments: dict[str, str] | None = None
    ) -> types.GetPromptResult:
        if name != "simple":
            raise ValueError(f"Unknown prompt: {name}")

        if arguments is None:
            arguments = {}

        return types.GetPromptResult(
            messages=create_messages(
                context=arguments.get("context"), topic=arguments.get("topic")
            ),
            description="A simple prompt with optional context and topic arguments",
        )        


    @app.list_resources()
    async def list_resources() -> list[types.Resource]:
        return [
            types.Resource(
                uri=AnyUrl(f"file:///{name}.txt"),
                name=name,
                description=f"A sample text resource named {name}",
                mimeType="text/plain",
            )
            for name in SAMPLE_RESOURCES.keys()
        ]

    @app.read_resource()
    async def read_resource(uri: AnyUrl) -> str | bytes:
        if uri.path is None:
            raise ValueError(f"Invalid resource path: {uri}")
        name = uri.path.replace(".txt", "").lstrip("/")

        if name not in SAMPLE_RESOURCES:
            raise ValueError(f"Unknown resource: {uri}")

        return SAMPLE_RESOURCES[name]

    if transport == "sse":
        from mcp.server.sse import SseServerTransport
        from starlette.applications import Starlette
        from starlette.responses import Response
        from starlette.routing import Mount, Route

        sse = SseServerTransport("/messages/")

        async def handle_sse(request):
            async with sse.connect_sse(
                request.scope, request.receive, request._send
            ) as streams:
                await app.run(
                    streams[0], streams[1], app.create_initialization_options()
                )
            return Response()

        starlette_app = Starlette(
            debug=True,
            routes=[
                Route("/sse", endpoint=handle_sse, methods=["GET"]),
                Mount("/messages/", app=sse.handle_post_message),
            ],
        )

        import uvicorn

        uvicorn.run(starlette_app, host="127.0.0.1", port=port)
    else:
        from mcp.server.stdio import stdio_server

        async def arun():
            async with stdio_server() as streams:
                await app.run(
                    streams[0], streams[1], app.create_initialization_options()
                )

        anyio.run(arun)

    return 0


if __name__ == "__main__":
    sys.exit(main())