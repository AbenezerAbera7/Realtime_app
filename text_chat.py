# text_chat.py
import json
import asyncio
from websocket_utils import connect_websocket, receive_events

def build_text_item_create(user_text):
    """Creates a conversation.item.create payload for user text."""
    return {
        "type": "conversation.item.create",
        "item": {
            "type": "message",
            "role": "user",
            "content": [{"type": "input_text", "text": user_text}]
        }
    }

async def send_text_and_get_text_response(user_text, instructions="Please respond in text only."):
    """Send text to OpenAI and get a text response."""
    ws = await connect_websocket()
    if not ws:
        return None
    item_create_payload = build_text_item_create(user_text)
    await ws.send(json.dumps(item_create_payload))
    response_create = {"type": "response.create", "response": {"instructions": instructions}}
    await ws.send(json.dumps(response_create))
    collected_text = []
    async for event in receive_events(ws, timeout=60):
        if event.get("type") == "response.text.delta":
            collected_text.append(event.get("delta", ""))
        elif event.get("type") == "response.text.done":
            return "".join(collected_text)
    return None
