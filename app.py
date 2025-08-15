if __name__ == "__main__":
    print("Starting server")
    import logging

    # Enable or disable debug logging
    DEBUG_LOGGING = False

    if DEBUG_LOGGING:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING)


from RealtimeTTS import (
    TextToAudioStream,
    OpenAIEngine,
)

from fastapi.responses import StreamingResponse, HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Query, Request
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from markdownify import markdownify as md

from queue import Queue
import threading
import logging
import uvicorn
import wave
import io
import os
import re
from dotenv import load_dotenv

load_dotenv()

PORT = int(os.environ.get("TTS_FASTAPI_PORT", 8000))

play_text_to_speech_semaphore = threading.Semaphore(1)
engine = None
speaking_lock = threading.Lock()
tts_lock = threading.Lock()
gen_lock = threading.Lock()


class TTSRequestHandler:
    def __init__(self, engine):
        self.engine = engine
        self.audio_queue = Queue()
        self.stream = TextToAudioStream(
            engine, on_audio_stream_stop=self.on_audio_stream_stop, muted=True
        )
        self.speaking = False

    def on_audio_chunk(self, chunk):
        self.audio_queue.put(chunk)

    def on_audio_stream_stop(self):
        self.audio_queue.put(None)
        self.speaking = False

    def play_text_to_speech(self, text):
        self.speaking = True
        self.stream.feed(text)
        logging.debug(f"Playing audio for text: {text}")
        print(f'Synthesizing: "{text}"')
        self.stream.play_async(on_audio_chunk=self.on_audio_chunk, muted=True)

    def audio_chunk_generator(self, send_wave_headers):
        first_chunk = False
        try:
            while True:
                chunk = self.audio_queue.get()
                if chunk is None:
                    print("Terminating stream")
                    break
                if not first_chunk:
                    if send_wave_headers:
                        print("Sending wave header")
                        yield create_wave_header_for_engine(self.engine)
                    first_chunk = True
                yield chunk
        except Exception as e:
            print(f"Error during streaming: {str(e)}")


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


def create_wave_header_for_engine(engine):
    _, _, sample_rate = engine.get_stream_info()

    num_channels = 1
    sample_width = 2
    frame_rate = sample_rate

    wav_header = io.BytesIO()
    with wave.open(wav_header, "wb") as wav_file:
        wav_file.setnchannels(num_channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(frame_rate)

    wav_header.seek(0)
    wave_header_bytes = wav_header.read()
    wav_header.close()

    final_wave_header = io.BytesIO()
    final_wave_header.write(wave_header_bytes)
    final_wave_header.seek(0)

    return final_wave_header.getvalue()


current_request_handler = None


@app.get("/tts")
async def tts(request: Request, text: str = Query(...), speed: float = Query(1.0)):
    global current_request_handler
    with tts_lock:
        engine.set_speed(speed)
        current_request_handler = TTSRequestHandler(engine)

        if play_text_to_speech_semaphore.acquire(blocking=False):
            try:
                # Remove markdown links, keeping only the link text
                processed_text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)

                threading.Thread(
                    target=current_request_handler.play_text_to_speech,
                    args=(processed_text,),
                    daemon=True,
                ).start()
            finally:
                play_text_to_speech_semaphore.release()

        return StreamingResponse(
            current_request_handler.audio_chunk_generator(True),
            media_type="audio/wav",
        )


@app.post("/stop")
async def stop_tts():
    global current_request_handler
    if current_request_handler and current_request_handler.speaking:
        current_request_handler.stream.stop()
        current_request_handler.speaking = False
        return {"status": "stopped"}
    return {"status": "not speaking"}


class HTMLContent(BaseModel):
    html: str

@app.post("/html_to_markdown")
async def html_to_markdown(content: HTMLContent):
    markdown = md(content.html, heading_style="ATX")
    return {"markdown": markdown}


@app.get("/")
def root_page():
    content = f"""
    <!DOCTYPE html>
    <html>
        <head>
            <title>Real-time Text-to-Speech (OpenAI)</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background-color: #f8f9fa;
                    color: #343a40;
                    margin: 0;
                    padding: 0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                }}
                #container {{
                    width: 90%;
                    max-width: 600px;
                    margin: 20px auto;
                    background-color: #ffffff;
                    border-radius: 15px;
                    padding: 30px;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                }}
                h2 {{
                    color: #007bff;
                    text-align: center;
                    margin-bottom: 20px;
                }}
                label {{
                    font-weight: 600;
                    margin-bottom: 5px;
                    display: block;
                }}
                select, textarea, button {{
                    width: 100%;
                    padding: 12px;
                    margin-bottom: 20px;
                    border: 1px solid #ced4da;
                    border-radius: 8px;
                    box-sizing: border-box;
                    font-size: 16px;
                }}
                button {{
                    background-color: #007bff;
                    color: #ffffff;
                    border: none;
                    cursor: pointer;
                    transition: background-color 0.3s;
                }}
                button:hover {{
                    background-color: #0056b3;
                }}
                audio {{
                    width: 100%;
                    margin-top: 20px;
                }}
                #speed-container {{
                    display: flex;
                    align-items: center;
                    gap: 15px;
                    margin-bottom: 20px;
                }}
                #speed {{
                    flex-grow: 1;
                }}
            </style>
        </head>
        <body>
            <div id="container">
                <h2>Real-time Text-to-Speech (OpenAI)</h2>
                <p>Adjust the reading speed and enter some text to begin.</p>
                <label for="speed">Reading Speed:</label>
                <div id="speed-container">
                    <input type="range" id="speed" name="speed" min="0.5" max="2.0" value="1.0" step="0.1">
                    <span id="speed-value">1.0x</span>
                </div>
                <label for="text">Text:</label>
                <textarea id="text" rows="4" placeholder="Enter text here..."></textarea>
                <button id="speakButton">Speak</button>
                <audio id="audio" controls></audio>
            </div>
            <script src="/static/tts.js"></script>
        </body>
    </html>
    """
    return HTMLResponse(content=content)


if __name__ == "__main__":
    print("Initializing TTS Engine")
    engine = OpenAIEngine(response_format="pcm")
    print("Server ready")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
