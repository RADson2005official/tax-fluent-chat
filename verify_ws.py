import asyncio
import websockets
import json
import sys

async def test_websocket():
    uri = "ws://localhost:8000/api/ws/test-client"
    try:
        async with websockets.connect(uri, origin=websockets.typing.Origin("http://localhost:5173")) as websocket:
            print(f"Connected to {uri}")
            
            # Send a test message
            test_msg = "Hello from verification script"
            await websocket.send(test_msg)
            print(f"Sent: {test_msg}")
            
            # Receive echo
            response = await websocket.recv()
            print(f"Received: {response}")
            
            if f"Message text was: {test_msg}" in response:
                print("Verification SUCCESS: Echo received")
            else:
                print("Verification FAILED: Unexpected response")
                
    except Exception as e:
        print(f"Verification FAILED: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_websocket())
