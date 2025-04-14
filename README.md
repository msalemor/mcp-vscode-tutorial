# mcp-vscode-tutorial
A tutorial to build an MCP server and use vscode as an MCP client

## Overview

Most MCP tutorials and demos are currently targeting the Claude Desktop application. However, you can also perform development and testing if you have GitHub Copilot with Agent mode. 

MCP servers are being written in many languages. This demo implements a sample MCP server in Go becuse the build process generates a small executable that requires no additional parameters to run.

## MCP Server code

For my testing, I used the following sample code:

- Go package: `mcp-go`
- Server code: [mcp-go/examples/everything](https://github.com/mark3labs/mcp-go/blob/main/examples/everything/main.go)

## Requirements

- Visual Studio Code
- Github Copilot with Agent mode

## Building the code in Windows

Note: you can clone the repo and perform other steps, but these are the ones I followed:

- Created a new folder: `mkdir mcpgo1`
- Created a new Golang module: `go mod init mcpgo1`
- Created a main file: `touch main.go`
- Copied the server code into the main.go file
- Got the required packages: `go mod tidy`
- Built the mcp server: `go build .`

## Deploying the server

- Open Github Copilot Chat
- Make sure that you are in Agent mode
- Click on tools
- Following this steps will create a file like this one:

```json
{
    "servers": {
        "mcpgo1": {
            "type": "stdio",
            "command": "D:\\github\\temp\\mcpgo1\\mcpgo1.exe",
            "args": []
        }
    }
}
```
