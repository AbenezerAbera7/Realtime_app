# OpenAI Realtime Audio & Text Chat Application

This repository provides a Gradio-based application to interact with OpenAI's Realtime API using both **audio and text inputs**. The app enables users to:
1. Record or upload audio and receive audio responses from the AI.
2. Type a message and get a short text response from the AI.

---

## Features

### 1. **Audio Chat**
- **Input**: Record your voice or upload an audio file.
- **Output**: The AI processes the input and replies with an audio response.
- **Use Case**: Engaging in voice-based conversations with AI.

### 2. **Text Chat**
- **Input**: Type a text message in the provided textbox.
- **Output**: The AI provides a concise, text-based reply.
- **Use Case**: Text-based queries or short conversational exchanges.

---


## Getting Started

### Prerequisites

Ensure you have the following installed:

- Python 3.7 or above
- Virtual Environment (recommended)
- API key from OpenAI with access to the realtime API
- Packages listed in the `requirements.txt` (see below for details)

### Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/AbenezerAbera7/Realtime_app
   cd Realtime_app
   ```

2. **Create and activate a virtual environment**:

   - On macOS and Linux:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     python -m venv venv
     .\venv\Scripts\activate
     ```

3. **Install the dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the environment variables**:

   Create a `.env` file in the project's root directory and add your OpenAI API key:
   
   ```
   OPENAI_API_KEY=your-openai-api-key
   ```

### Usage

1. **Run the application**:

   ```bash
   python/python3 main.py
   ```

2. **Access the Gradio Interface**:

   The application will start locally and print a URL (e.g., `http://127.0.0.1:7860/`) in the terminal.

   Open this URL in a web browser to access the app.



# How to Use

### **Audio Chat**
1. Navigate to the **"Audio Chat"** tab.
2. Record your voice or upload an audio file.
3. Click the **"Send Audio"** button to process your input.
4. Listen to the AI's audio response in the **"AI's Audio Reply"** section.

### **Text Chat**
1. Navigate to the **"Text Chat"** tab.
2. Type a message in the **"Your Text Input"** textbox.
3. Click the **"Send Text"** button.
4. View the AI's response in the **"AI's Text Response"** section.

# **Author**

- [Abenezer Abera](https://github.com/AbenezerAbera7).
