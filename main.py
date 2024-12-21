import os
import io
import json
import asyncio
import base64

import websockets
import soundfile as sf
from pydub import AudioSegment
import gradio as gr
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

WEBSOCKET_URL = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01"
HEADERS = {
    "Authorization": f"Bearer {OPENAI_API_KEY}",
    "openai-beta": "realtime=v1"
}

# -----------------------------------------------------------------------------
# SHARED WEBSOCKET FUNCTION
# -----------------------------------------------------------------------------
async def connect_to_openai_ws(payload_event, is_audio=True, timeout=60, retries=3):
    """Handles WebSocket communication for both audio and text."""
    if not OPENAI_API_KEY:
        print("API Key not found!")
        return None

    for attempt in range(retries):
        try:
            async with websockets.connect(WEBSOCKET_URL, extra_headers=HEADERS) as ws:
                print(f"Connected to server. (Audio = {is_audio})")

                # Send 'conversation.item.create'
                await ws.send(payload_event)
                print("conversation.item.create sent.")

                # Build 'response.create' request
                if is_audio:
                    response_instructions = "Please respond with audio to the user's input."
                    response_obj = {"voice": "alloy"}
                else:
                    response_instructions = "Please respond in text only, under 50 words."
                    response_obj = {"modalities": ["text"]}

                response_create = {
                    "type": "response.create",
                    "response": {
                        "instructions": response_instructions,
                        **response_obj
                    }
                }
                await ws.send(json.dumps(response_create))
                print("response.create command sent.")

                # Process events until complete
                audio_data_list = []
                text_collected = []

                while True:
                    try:
                        message = await asyncio.wait_for(ws.recv(), timeout=timeout)
                        event = json.loads(message)
                        print("Parsed event:", event)

                        if is_audio:
                            if event.get('type') == 'response.audio.delta':
                                audio_data_list.append(event['delta'])
                            elif event.get('type') == 'response.audio.done':
                                print("Received full AUDIO response.")
                                base64_data = "".join(audio_data_list)
                                return base64.b64decode(base64_data)
                        else:
                            if event.get('type') == 'response.text.delta':
                                text_collected.append(event.get("delta", ""))
                            elif event.get('type') == 'response.text.done':
                                print("Received full TEXT response.")
                                return "".join(text_collected)
                    except asyncio.TimeoutError:
                        print(f"Timeout after {timeout} seconds. (Audio={is_audio})")
                        break
        except websockets.exceptions.ConnectionClosed as e:
            print(f"WebSocket closed: {e.code} - {e.reason}")
        except Exception as e:
            print(f"Unexpected error: {e}")
        print(f"Retrying... (Audio={is_audio}) Attempt {attempt+1}/{retries}")

    print(f"Failed after max retries. (Audio={is_audio})")
    return None

# -----------------------------------------------------------------------------
# AUDIO CHAT LOGIC
# -----------------------------------------------------------------------------
def numpy_to_audio_bytes(audio_np, sample_rate):
    """Convert (sample_rate, np.array) into WAV bytes."""
    with io.BytesIO() as buffer:
        sf.write(buffer, audio_np, samplerate=sample_rate, format='WAV')
        buffer.seek(0)
        return buffer.read()

def audio_to_item_create_event(audio_data):
    """Build conversation.item.create for audio input."""
    sample_rate, audio_np = audio_data
    wav_bytes = numpy_to_audio_bytes(audio_np, sample_rate)
    base64_pcm = base64.b64encode(wav_bytes).decode('utf-8')
    return json.dumps({
        "type": "conversation.item.create",
        "item": {
            "type": "message",
            "role": "user",
            "content": [{"type": "input_audio", "audio": base64_pcm}]
        }
    })

def voice_chat_response(audio_data, history):
    """Gradio callback for audio input -> audio response."""
    try:
        if not audio_data:
            return None, history
        audio_event = audio_to_item_create_event(audio_data)
        audio_response = asyncio.run(connect_to_openai_ws(audio_event, is_audio=True, timeout=60))
        if isinstance(audio_response, bytes):
            audio_seg = AudioSegment.from_raw(io.BytesIO(audio_response), sample_width=2, frame_rate=24000, channels=1)
            buffer_wav = io.BytesIO()
            audio_seg.export(buffer_wav, format="wav")
            return buffer_wav.getvalue(), history
        return None, history
    except Exception as e:
        print("Error in voice_chat_response:", e)
        return None, history

# -----------------------------------------------------------------------------
# TEXT CHAT LOGIC
# -----------------------------------------------------------------------------
def build_text_item_create_event(user_text):
    """Build conversation.item.create for text input."""
    return json.dumps({
        "type": "conversation.item.create",
        "item": {
            "type": "message",
            "role": "user",
            "content": [{"type": "input_text", "text": user_text}]
        }
    })

def text_chat_response(user_text):
    """Gradio callback for text input -> text response."""
    try:
        if not user_text:
            return "No input text."
        text_event = build_text_item_create_event(user_text)
        text_response = asyncio.run(connect_to_openai_ws(text_event, is_audio=False, timeout=60))
        return text_response if text_response else "No text response received."
    except Exception as e:
        print("Error in text_chat_response:", e)
        return str(e)

# -----------------------------------------------------------------------------
# GRADIO APP
# -----------------------------------------------------------------------------
with gr.Blocks(title="OpenAI Realtime - Audio & Text") as demo:
    gr.Markdown("<h1 style='text-align: center;'>OpenAI Realtime: Audio & Text</h1>")
    with gr.Tab("Audio Chat"):
        gr.Markdown("#### Record or upload audio, get an **audio response**.")
        audio_input = gr.Audio(label="Audio Input (Record or Upload)", type="numpy")
        audio_output = gr.Audio(label="AI's Audio Reply", autoplay=True)
        history_state = gr.State([])
        audio_button = gr.Button("Send Audio")
        audio_button.click(fn=voice_chat_response, inputs=[audio_input, history_state], outputs=[audio_output, history_state])
    with gr.Tab("Text Chat"):
        gr.Markdown("#### Type your message, get a **short text** response.")
        text_input = gr.Textbox(label="Your Text Input")
        text_output = gr.Textbox(label="AI's Text Response")
        text_button = gr.Button("Send Text")
        text_button.click(fn=text_chat_response, inputs=text_input, outputs=text_output)

if __name__ == "__main__":
    demo.launch()
