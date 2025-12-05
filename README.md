# AI Interview Bot V2

An AI-powered technical interview system that conducts interactive interviews using speech recognition, natural language processing, and text-to-speech capabilities.

## Features

- **Voice-based Interview**: Record answers using your microphone
- **Real-time Transcription**: Uses OpenAI Whisper for accurate speech-to-text
- **AI Evaluation**: Powered by Google's Gemini 2.0 Flash for intelligent answer assessment
- **Text-to-Speech**: Speaks questions and feedback aloud
- **Two Interview Modes**: Role-based or Resume-based interviews
- **Follow-up Questions**: Generates contextual follow-up questions based on your answers
- **Comprehensive Feedback**: Provides detailed evaluation and improvement suggestions

## Prerequisites

- Python 3.8 or higher
- Microphone access
- Internet connection (for Gemini API)
- Google Gemini API key

## Required Libraries

### Option 1: Individual Installation

Install each package individually:

```bash
pip install numpy
pip install sounddevice
pip install openai-whisper
pip install scipy
pip install pyttsx3
pip install google-generativeai
pip install python-dotenv
pip install langgraph
```

### Option 2: Batch Installation

Install all packages in one command:

```bash
pip install numpy sounddevice openai-whisper scipy pyttsx3 google-generativeai python-dotenv langgraph
```

### Option 3: Using requirements.txt

Create a `requirements.txt` file with the following content:

```
numpy>=1.21.0
sounddevice>=0.4.0
openai-whisper>=20231117
scipy>=1.7.0
pyttsx3>=2.90
google-generativeai>=0.3.0
python-dotenv>=0.19.0
langgraph>=0.0.20
```

Then install all dependencies:

```bash
pip install -r requirements.txt
```

## Setup Instructions

### 1. Clone or Download the Repository

```bash
git clone https://github.com/Amaanudeen/ai_interview_bot.git
cd ai_interview_bot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Create a `.env` file in the project root directory:

```bash
# .env file
GEMINI_API_KEY="your-gemini-api-key-here"
```

**How to get a Gemini API Key:**
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the key and paste it in your `.env` file

### 4. Configure Audio Device (Optional)

The bot uses audio device index 8 by default. If you encounter audio issues:

1. List available audio devices:
```python
import sounddevice as sd
print(sd.query_devices())
```

2. Update the `audio_device_index` in the `main()` function of `ai_interview_bot_v2.py`

### 5. Test Whisper Model Download

The first run will download the Whisper "small" model (~244 MB). Ensure you have:
- Stable internet connection
- At least 1GB free disk space
- Write permissions in the Python environment

## Usage

### Running the Interview Bot

```bash
python ai_interview_bot_v2.py
```

### Interview Flow

1. **Mode Selection**: Choose between role-based or resume-based interview
2. **Question Phase**: The bot asks technical questions
3. **Recording**: Use voice commands to record your answers:
   - Type `start` to begin recording
   - Speak your answer clearly
   - Type `stop` to end recording and transcribe
   - Type `quit` to exit early
4. **Evaluation**: The AI evaluates your answer and may ask follow-ups
5. **Feedback**: Receive comprehensive feedback at the end

### Voice Commands

- `start` - Begin recording your answer
- `stop` - Stop recording and process your response
- `quit` - Exit the interview early

## Configuration Options

You can modify these settings in the `InterviewConfig` class:

- `max_questions`: Maximum number of main questions (default: 10)
- `sample_rate`: Audio sample rate (default: 16000 Hz)
- `whisper_model`: Whisper model size ("tiny", "base", "small", "medium", "large")
- `gemini_model`: Gemini model version (default: "gemini-2.0-flash")

## Troubleshooting

### Common Issues

**1. Microphone Not Working**
- Check microphone permissions
- Ensure no other application is using the microphone
- Try different audio device index

**2. Whisper Model Download Fails**
- Check internet connection
- Ensure sufficient disk space
- Try a smaller model ("tiny" or "base")

**3. Gemini API Errors**
- Verify API key is correct
- Check API quota and billing
- Ensure stable internet connection

**4. Audio Device Errors**
```python
# List available devices
import sounddevice as sd
print(sd.query_devices())
```

**5. TTS Not Working**
- Install additional TTS engines if needed
- Check system audio output
- Try different TTS rate/volume settings

### Performance Tips

- Use "small" Whisper model for balance of speed and accuracy
- Ensure quiet environment for better transcription
- Speak clearly and at moderate pace
- Use a good quality microphone

## System Requirements

- **OS**: Windows, macOS, or Linux
- **RAM**: Minimum 4GB (8GB recommended)
- **Storage**: 2GB free space (for Whisper models)
- **Audio**: Microphone and speakers/headphones
- **Network**: Internet connection for AI processing

## File Structure

```
ai_interview_bot/
├── ai_interview_bot_v2.py    # Main application file
├── .env                      # Environment variables
├── README.md                 # This file
└── requirements.txt          # Python dependencies
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source. Please check the repository for license details.

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the error messages carefully
3. Ensure all dependencies are properly installed
4. Verify your API keys and environment setup

---

**Note**: This bot requires active internet connection for AI processing and may incur costs based on Gemini API usage.
