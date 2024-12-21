# podcast_generator.py

import asyncio
import json
from websocket_utils import connect_websocket, receive_events

async def main():
    ws = await connect_websocket(timeout=30)
    if not ws:
        return

    # Example: send some text or audio
    item_create_event = {
        "type": "conversation.item.create",
        "item": {
            "type": "message",
            "role": "user",
            "content": [{"type": "input_text", "text": "This is a podcast test."}]
        }
    }
    await ws.send(json.dumps(item_create_event))

    # Instruct the model to produce an audio or text response
    response_create = {
        "type": "response.create",
        "response": {
            "instructions": "Please generate an audio summary for the podcast."
        }
    }
    await ws.send(json.dumps(response_create))

    audio_parts = []
    async for event in receive_events(ws, timeout=60):
        print("Podcast Generator - Received event:", event)
        if event.get('type') == 'response.audio.delta':
            audio_parts.append(event['delta'])
        elif event.get('type') == 'response.audio.done':
            print("Podcast audio done.")
            # Combine and do something with audio_parts
            break

if __name__ == "__main__":
    asyncio.run(main())
