# import asyncio
# from fastmcp import Client


# async def test_mcp():
#     # Connect to your server (trailing slash optional; client handles it)
#     client = Client("http://localhost:8002/sse")
#     async with client:
#         # Step 1: Ping the server (basic connectivity)
#         await client.ping()
#         print("✅ Server ping successful!")

#         # Step 2: List tools (should show get_campaign, trigger_campaign, update_smart_list)
#         # tools = await client.list_tools()
#         # print("Available tools:", tools)
#         print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
#         # Step 3: Call a read-only tool (replace 123 with a real campaign ID from Marketo)
#         #result = await client.call_tool("get_leads_by_filter_type", {"filter_type": "email", "filter_values": ["Munnim@grazitti.com"], "fields": ["id", "email", "first_name", "last_name", "company"], "batch_size": 100})
#         #print("get_campaign result:", result)
#         # objects = await client.call_tool("list_objects", {})
#         #print(objects)

#         result = await client.call_tool("run_soql", {"soql": "SELECT Id, Name FROM Account LIMIT 5"})
#         print(result)

#         # Optional: Test trigger_campaign (side-effecting; use real data cautiously)
#         # payload = {"input": [{"id": your_lead_id}]}  # Uncomment with valid payload
#         # trigger_result = await client.call_tool("trigger_campaign", {
#         #     "campaign_id": 123,
#         #     "input_payload": payload
#         # })
#         # print("trigger_campaign result:", trigger_result)

# if __name__ == "__main__":
#     asyncio.run(test_mcp())

import asyncio
from fastmcp import Client

async def test_odata_query():
    client = Client("http://localhost:8002/sse")
    async with client:
        await client.ping()
        print("✅ Server ping successful!")

        # Proper OData query
        odata_query = "accounts?$select=name,accountid&$top=5"
        try:
            result = await client.call_tool("run_odata_query", {"odata_query": odata_query})
            print("Query result:", result)
        except Exception as e:
            print("❌ Error running OData query:", e)

if __name__ == "__main__":
    asyncio.run(test_odata_query())
