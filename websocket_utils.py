# websocket_utils.py

import os
import json
import asyncio
import websockets
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
WEBSOCKET_URL = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "openai-beta": "realtime=v1"
}

async def connect_websocket(timeout=60):
    """Establish a WebSocket connection to OpenAI's realtime API."""
    if not API_KEY:
        print("Error: OPENAI_API_KEY not found in environment!")
        return None

    try:
        ws = await asyncio.wait_for(
            websockets.connect(WEBSOCKET_URL, extra_headers=HEADERS),
            timeout=timeout
        )
        print("Connected to OpenAI Realtime WebSocket.")
        return ws
    except (asyncio.TimeoutError, Exception) as e:
        print(f"Failed to connect: {e}")
        return None

async def receive_events(ws, timeout=60):
    """Yield events from the WebSocket until timeout or close."""
    while True:
        try:
            message = await asyncio.wait_for(ws.recv(), timeout=timeout)
            event = json.loads(message)
            yield event
        except asyncio.TimeoutError:
            print(f"No response received within {timeout} seconds.")
            return
        except websockets.exceptions.ConnectionClosed:
            print("WebSocket connection closed.")
            return
        except Exception as e:
            print(f"Unexpected error receiving event: {e}")
            return
