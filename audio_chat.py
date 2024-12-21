# audio_chat.py

import io
import json
import base64
import asyncio
import soundfile as sf
from pydub import AudioSegment
from websocket_utils import connect_websocket, receive_events

def numpy_to_audio_bytes(audio_np, sample_rate):
    """Convert NumPy audio data to WAV bytes in memory."""
    with io.BytesIO() as buffer:
        sf.write(buffer, audio_np, samplerate=sample_rate, format='WAV')
        buffer.seek(0)
        return buffer.read()

def build_audio_item_create(sample_rate, audio_np):
    """Creates a conversation.item.create payload for user audio."""
    audio_bytes = numpy_to_audio_bytes(audio_np, sample_rate)
    pcm_base64 = base64.b64encode(audio_bytes).decode('utf-8')
    event = {
        "type": "conversation.item.create",
        "item": {
            "type": "message",
            "role": "user",
            "content": [{
                "type": "input_audio",
                "audio": pcm_base64
            }]
        }
    }
    return event

async def send_audio_and_get_audio_response(sample_rate, audio_np, instructions="Please respond with audio."):
    """
    Sends audio to OpenAI, then requests an audio response.
    Returns the final combined audio bytes (PCM16) or None.
    """
    ws = await connect_websocket()
    if not ws:
        return None

    # Step 1: Send conversation.item.create for user audio
    item_create_payload = build_audio_item_create(sample_rate, audio_np)
    await ws.send(json.dumps(item_create_payload))
    print("Audio item_create event sent.")

    # Step 2: Instruct the server to produce an audio response
    response_create = {
        "type": "response.create",
        "response": {
            "voice": "alloy",
            "instructions": instructions
        }
    }
    await ws.send(json.dumps(response_create))
    print("response.create event sent.")

    audio_data_list = []

    async for event in receive_events(ws, timeout=60):
        print("Audio Chat - Received event:", event)

        # Collect incremental audio data
        if event.get('type') == 'response.audio.delta':
            audio_data_list.append(event['delta'])

        elif event.get('type') == 'response.audio.done':
            print("Audio Chat - Audio response completed.")
            full_audio_base64 = "".join(audio_data_list)
            return base64.b64decode(full_audio_base64)

        elif event.get('type') == 'error':
            print("Audio Chat - Error event:", event)
            break

    return None

def pcm16_to_wav(audio_bytes):
    """Convert raw PCM16 data to playable WAV bytes."""
    with io.BytesIO(audio_bytes) as buffer:
        audio_segment = AudioSegment.from_raw(
            buffer,
            sample_width=2,
            frame_rate=24000,
            channels=1
        )
        wav_buffer = io.BytesIO()
        audio_segment.export(wav_buffer, format="wav")
        return wav_buffer.getvalue()
