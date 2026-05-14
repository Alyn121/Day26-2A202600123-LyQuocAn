import asyncio
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def verify():
    # Create server parameters for stdio connection
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["mcp_server.py"],
        env=None
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()

            # List resources
            resources = await session.list_resources()
            print("Resources available:", [r.uri for r in resources.resources])

            # Read full schema resource
            schema_res = await session.read_resource("schema://database")
            print("\n--- Full Schema ---")
            print(schema_res.contents[0].text[:200] + "...")

            # List tools
            tools = await session.list_tools()
            print("\nTools available:", [t.name for t in tools.tools])

            # Call search tool
            print("\n--- Testing search tool ---")
            result = await session.call_tool("search", {"table": "students", "limit": 2})
            print(result.content[0].text)

            # Call search tool with filter
            print("\n--- Testing search tool with filter ---")
            result = await session.call_tool("search", {
                "table": "students", 
                "filters": [{"column": "cohort", "operator": "=", "value": "A1"}]
            })
            print(result.content[0].text)
            
            # Call aggregate tool
            print("\n--- Testing aggregate tool ---")
            result = await session.call_tool("aggregate", {"table": "students", "agg_func": "COUNT"})
            print(result.content[0].text)
            
            # Call insert tool
            print("\n--- Testing insert tool ---")
            result = await session.call_tool("insert", {
                "table": "courses",
                "data": {"title": "Computer Science 101", "credits": 4}
            })
            print(result.content[0].text)
            
            # Test invalid request
            print("\n--- Testing invalid request ---")
            result = await session.call_tool("search", {"table": "invalid_table"})
            print(result.content[0].text)

if __name__ == "__main__":
    asyncio.run(verify())
