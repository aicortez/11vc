# Voice Changer

A voice changer application using ElevenLabs' speech-to-speech technology. Record your voice and transform it using various AI-powered voices.

## Features

- Quick voice transformation (1-2 second processing delay)
- Multiple AI voices to choose from
- Customizable recording key (default: Mouse4)
- System default or custom audio device selection
- ElevenLabs credit usage tracking
- Simple console interface

## Prerequisites

- Python 3.10 or higher
- An ElevenLabs API key ([Get it here](https://elevenlabs.io/app/settings/api-keys))
- Microphone for audio input
- Speakers/headphones for audio output

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/aicortez/11vc.git
   cd voice-changer
   ```

2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the script:
   ```bash
   python voice_changer.py
   ```

2. First-time setup:
   - Enter your ElevenLabs API key when prompted
   - Configure input/output devices if needed (or use system defaults)
   - Select your preferred voice
   - Choose a recording key (default: Mouse4)

3. Using the voice changer:
   - Hold the recording key to capture audio
   - Release to process and play back with the selected voice
   - Use number keys to navigate menus:
     - `0`: Stop voice changer
     - `4`: Change voice
     - `q`: Quit application

## Settings Menu

The application provides several configuration options:
1. Change input device
2. Change output device
3. Change recording key
4. Change voice
5. Start voice changer
6. Change API key

## Dependencies

- elevenlabs
- pyaudio
- pynput
- pygame

## Support

If you encounter any issues or have questions:
1. Check the [Issues](https://github.com/aicortez/11vc/issues) page
2. Create a new issue if needed
3. Provide as much detail as possible about your problem

## Disclaimer

This application requires an ElevenLabs API key and may incur usage charges. Please review ElevenLabs' pricing and terms before use.
