# Python MCP Server

## Overview

This Python MCP (Model Context Protocol) server provides an interface for querying and interacting with Azure Data Explorer (Kusto) databases. Built using the MCP framework, it enables seamless integration with AI assistants and other MCP-compatible clients to execute Kusto queries and retrieve data programmatically.

The server implements MCP tools that allow clients to:
- Connect to Azure Kusto clusters
- Execute KQL (Kusto Query Language) queries
- Retrieve and process query results
- Handle authentication and authorization

This implementation leverages the `azure-kusto-data` library for database connectivity and the `mcp` package for protocol handling, providing a robust solution for integrating Kusto data access into MCP-enabled applications.

## Requirements

- uv package manager
- Python 3.11+
- click
- mcp[mci]
- azure-kusto-data
