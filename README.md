# RealtimeTTS Web Interface

This project provides a simple web-based interface for the [RealtimeTTS](https://github.com/KoljaB/RealtimeTTS) library, specifically utilizing the OpenAI engine for text-to-speech conversion. It allows you to enter text, adjust the speaking speed, and listen to the generated audio in real-time.

This is a fork of the original [RealtimeTTS](https://github.com/KoljaB/RealtimeTTS) project.

## Features

*   **Web-Based UI**: A clean and simple interface to interact with the TTS engine.
*   **Real-time Audio Streaming**: Audio is streamed from the server to the client as it's generated.
*   **Adjustable Speaking Speed**: Control the speed of the speech from 0.5x to 2.0x.
*   **Stop Functionality**: Interrupt the audio playback at any time.
*   **HTML to Markdown on Paste**: Automatically converts rich text pasted into the text area into clean Markdown.

## How It Works

The application is built with a Python backend and a vanilla JavaScript frontend:

*   **Backend**: A [FastAPI](https://fastapi.tiangolo.com/) server (`app.py`) that handles the text-to-speech generation using the `RealtimeTTS` library with the `OpenAIEngine`. It exposes endpoints to start the TTS stream (`/tts`), stop it (`/stop`), and convert HTML to Markdown (`/html_to_markdown`).
*   **Frontend**: A single HTML page with JavaScript (`static/tts.js`) that communicates with the backend. It captures user input, sends requests to the server, and plays the received audio stream in the browser.

## Installation and Setup

Follow these steps to get the application running on your local machine.

### 1. Clone the Repository

```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Create and Activate a Virtual Environment

It's recommended to use a virtual environment to manage dependencies.

```bash
# For Windows
python -m venv venv
venv\Scripts\activate

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

Install all the required Python packages from `requirements.txt`.

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

The application requires an OpenAI API key to function.

1.  Create a file named `.env` in the root of the project directory.
2.  Add your OpenAI API key to the `.env` file:

    ```
    OPENAI_API_KEY="your-openai-api-key"
    ```

3.  (Optional) You can also specify the port on which the server will run:

    ```
    TTS_FASTAPI_PORT=8000
    ```

## Usage

1.  **Start the Server**:
    Run the `app.py` script from your terminal:
    ```bash
    python app.py
    ```

2.  **Access the Web Interface**:
    Open your web browser and navigate to:
    [http://localhost:8000](http://localhost:8000) (or the port you specified).

3.  **Use the Application**:
    *   Enter the text you want to convert to speech in the text area.
    *   Adjust the reading speed using the slider.
    *   Click the "Speak" button to start the audio.
    *   Click the "Stop" button to end the playback.

---

This fork focuses solely on providing this web interface. For more details on the underlying TTS library, please refer to the original [RealtimeTTS repository](https://github.com/KoljaB/RealtimeTTS).
