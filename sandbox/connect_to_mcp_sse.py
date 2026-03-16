import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client
import logging
import sys

# This will show us every JSON-RPC message going back and forth
logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger(__name__)
async def run_http_client():
    server_url = "http://localhost:5001/sse" # Ensure this is correct

    print(f"[*] Attempting to connect to {server_url}...")
    
    try:
        async with sse_client(url=server_url) as (read, write):
            async with ClientSession(read, write) as session:
                print("[*] Transport established. Starting initialization...")
                
                # Wrap initialization in a 10-second timeout
                await asyncio.wait_for(session.initialize(), timeout=10.0)
                
                print("[*] Successfully initialized!")
                
                # Try to list tools immediately to prove it works
                tools = await session.list_tools()
                print(f"[*] Found tools: {[t.name for t in tools.tools]}")

    except asyncio.TimeoutError:
        print("[!] ERROR: Initialization timed out. The server connected but didn't finish the handshake.")
    except Exception as e:
        print(f"[!] ERROR: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(run_http_client())