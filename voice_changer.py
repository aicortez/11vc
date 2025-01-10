import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pyaudio
import wave
from pynput import mouse, keyboard
from elevenlabs import ElevenLabs
import io
import threading
from pygame import mixer
from queue import Queue
from dotenv import load_dotenv

# Parameters
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
FRAMES_PER_BUFFER = 1024

# ElevenLabs API setup
API_KEY = None  # Initialize as None
client = None   # Initialize as None

# Remove or comment out this test block since it's too early
# try:
#     voices_list = client.voices.list()
#     print("Successfully connected to ElevenLabs API")
# except Exception as e:
#     print(f"Error connecting to ElevenLabs API: {e}")

# Voice dictionary
voices = {
    1: ('Aria', '9BWtsMINqrJLrRacOk9x'),
    2: ('Roger', 'CwhRBWXzGAHq8TQ4Fs17'),
    3: ('Sarah', 'EXAVITQu4vr4xnSDxMaL'),
    4: ('Laura', 'FGY2WhTYpPnrIDTdsKH5'),
    5: ('Charlie', 'IKne3meq5aSn9XLyUdCD'),
    6: ('George', 'JBFqnCBsd6RMkjVDRZzb'),
    7: ('Callum', 'N2lVS1w4EtoT3dr4eOWO'),
    8: ('River', 'SAz9YHcvj6GT2YYXdXww'),
    9: ('Liam', 'TX3LPaxmHKxFdv7VOQHJ'),
    10: ('Charlotte', 'XB0fDUnXU5powFXDhCwa'),
    11: ('Alice', 'Xb7hH8MSUJpSbSDYk0k2'),
    12: ('Matilda', 'XrExE9yKIg1WjnnlVkGX'),
    13: ('Will', 'bIHbv24MWmeRgasZH58o'),
    14: ('Jessica', 'cgSgspJ2msm6clMCkdW9'),
    15: ('Eric', 'cjVigY5qzO86Huf0OWal'),
    16: ('Chris', 'iP95p4xoKVk53GoZ742B'),
    17: ('Brian', 'nPczCjzI2devNBz1zQrb'),
    18: ('Daniel', 'onwK4e9ZLuTAKqWW03F9'),
    19: ('Lily', 'pFZP5JQG7iQjIQuC4Bku'),
    20: ('Bill', 'pqHfZKP75CvOlQylNhV4')
}

# At the top of the file with other initializations
def get_default_device_index(p, is_input=True):
    try:
        default_device_info = p.get_default_host_api_info()
        if is_input:
            return default_device_info.get('defaultInputDevice', None)
        else:
            return default_device_info.get('defaultOutputDevice', None)
    except Exception:
        return None

# Initialize default settings
current_voice = 1
VOICE_ID = voices[current_voice][1]
input_device_index = None  # Will use system default
output_device_index = None  # Will use system default
record_key = mouse.Button.x1  # Default to Mouse4

# Initialize PyAudio
p = pyaudio.PyAudio()

recording = False
frames = []
stop_flag = False

audio_queue = Queue()

# At the top of your file
load_dotenv()

def save_config():
    # Create or update .env file
    with open('.env', 'w') as f:
        f.write(f'ELEVENLABS_API_KEY={API_KEY}\n')

def load_config():
    global API_KEY, client
    
    # Try environment variable first
    api_key = os.getenv('ELEVENLABS_API_KEY')
    
    if api_key and validate_api_key(api_key):
        API_KEY = api_key
        client = ElevenLabs(api_key=API_KEY)
        return True
        
    return False

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def display_current_settings():
    clear_console()
    try:
        input_device_name = "System Default" if input_device_index is None else p.get_device_info_by_index(input_device_index)['name']
    except OSError:
        input_device_name = "System Default"
    
    try:
        output_device_name = "System Default" if output_device_index is None else p.get_device_info_by_index(output_device_index)['name']
    except OSError:
        output_device_name = "System Default"
    
    record_key_name = record_key.name if isinstance(record_key, mouse.Button) else record_key.char
    print("\n" + "="*50)
    print("Settings Menu")
    print(get_account_status())
    print("-"*50)
    print(f"Input Device: {input_device_name}")
    print(f"Output Device: {output_device_name}")
    print(f"Recording Key: {record_key_name}")
    print(f"Voice: {voices[current_voice][0]}")
    print(f"API Key: {'Configured' if API_KEY else 'Not Configured'}")
    print("="*50)

def list_audio_devices():
    input_devices = {}
    output_devices = {}

    # Find the index for MME host API
    mme_host_api_index = None
    for i in range(p.get_host_api_count()):
        host_api_info = p.get_host_api_info_by_index(i)
        if host_api_info['name'].lower() == 'mme':
            mme_host_api_index = i
            break

    if mme_host_api_index is None:
        print("MME host API not found.")
        return [], []

    for i in range(p.get_device_count()):
        device_info = p.get_device_info_by_index(i)
        # Check if the device belongs to the MME host API
        if device_info['hostApi'] == mme_host_api_index:
            normalized_name = device_info['name'].strip().lower()
            if device_info['maxInputChannels'] > 0 and normalized_name not in input_devices:
                input_devices[normalized_name] = (i, device_info['name'])
            if device_info['maxOutputChannels'] > 0 and normalized_name not in output_devices:
                output_devices[normalized_name] = (i, device_info['name'])

    print("Input Devices:", input_devices)
    print("Output Devices:", output_devices)
    return list(input_devices.values()), list(output_devices.values())

def select_input_device():
    global input_device_index
    input_devices, _ = list_audio_devices()

    clear_console()
    print("\n" + "="*50)
    print("Input Device Selection")
    print("Available input devices:")
    for idx, (index, name) in enumerate(input_devices):
        print(f"{idx}: {name}")
    print("="*50)
    
    input_choice = int(input("\nEnter the number of the input device: "))
    input_device_index = input_devices[input_choice][0]
    print(f"Selected input device: {input_devices[input_choice][1]}")
    display_current_settings()

def select_output_device():
    global output_device_index
    _, output_devices = list_audio_devices()

    clear_console()
    print("\n" + "="*50)
    print("Output Device Selection")
    print("Available output devices:")
    for idx, (index, name) in enumerate(output_devices):
        print(f"{idx}: {name}")
    print("="*50)
    
    output_choice = int(input("\nEnter the number of the output device: "))
    output_device_index = output_devices[output_choice][0]
    print(f"Selected output device: {output_devices[output_choice][1]}")
    display_current_settings()

def select_record_key():
    global record_key
    clear_console()
    print("\n" + "="*50)
    print("Recording Key Selection")
    print("Press any key or Mouse4/Mouse5 to select the recording key...")
    print("="*50 + "\n")
    
    selected_key = None
    stop_listeners = False

    def on_key_press(key):
        nonlocal stop_listeners, selected_key
        if key not in [keyboard.Key.esc, keyboard.Key.enter]:
            selected_key = key
        stop_listeners = True
        return False

    def on_mouse_click(x, y, button, pressed):
        nonlocal stop_listeners, selected_key
        if pressed and button in [mouse.Button.x1, mouse.Button.x2]:
            selected_key = button
        stop_listeners = True
        return False

    # Use threading to run both listeners simultaneously
    with keyboard.Listener(on_press=on_key_press) as k_listener, mouse.Listener(on_click=on_mouse_click) as m_listener:
        while not stop_listeners:
            pass

    if selected_key:
        key_name = selected_key.name if isinstance(selected_key, mouse.Button) else selected_key.char
        print(f"\nSelected key: {key_name}")
        print("Press Enter to confirm or Esc to cancel...")
        
        while True:
            with keyboard.Events() as events:
                event = events.get()
                if event.key == keyboard.Key.enter:
                    record_key = selected_key
                    print(f"Recording key set to: {key_name}")
                    break
                elif event.key == keyboard.Key.esc:
                    print("Cancelled. Recording key not changed.")
                    break

def get_account_status():
    try:
        user_info = client.user.get()
        subscription = user_info.subscription
        char_count = subscription.character_count
        char_limit = subscription.character_limit
        percentage = (char_count / char_limit * 100) if char_limit > 0 else 0
        return f"ElevenLabs Credits: {char_count:,}/{char_limit:,} ({percentage:.1f}%)"
    except AttributeError:
        # If we can't access the attributes directly, try accessing as dictionary
        try:
            subscription = user_info.get('subscription', {})
            char_count = subscription.get('character_count', 0)
            char_limit = subscription.get('character_limit', 0)
            percentage = (char_count / char_limit * 100) if char_limit > 0 else 0
            return f"ElevenLabs Credits: {char_count:,}/{char_limit:,} ({percentage:.1f}%)"
        except Exception as e:
            print(f"Error parsing subscription data: {e}")
            return "ElevenLabs Credits: Unable to fetch"
    except Exception as e:
        print(f"Error fetching credits: {e}")
        return "ElevenLabs Credits: Unable to fetch"

def validate_api_key(key):
    try:
        test_client = ElevenLabs(api_key=key)
        # Try to get user info to verify the key works
        user_info = test_client.user.get()
        return True
    except Exception as e:
        print(f"Invalid API key: {e}")
        return False

def set_api_key():
    global API_KEY, client
    clear_console()
    print("\n" + "="*50)
    print("ElevenLabs API Key Setup")
    print("Get your API key from: https://elevenlabs.io/app/settings/api-keys")
    print("="*50)
    
    key = input("\nEnter your ElevenLabs API key: ").strip()
    
    if validate_api_key(key):
        API_KEY = key
        client = ElevenLabs(api_key=API_KEY)
        print("API key validated successfully!")
        return True
    return False

def update_status_display(status_message, processing_details=None):
    clear_console()
    print("\n" + "="*50)
    print("Voice changer is active")
    print(f"Voice: {voices[current_voice][0]}")
    print(get_account_status())
    print(f"Press '{record_key}' to record")
    print(status_message)
    if processing_details:
        print(processing_details)
    print("="*50)
    print("\nEnter '0' to stop the voice changer or '4' to change the voice: ", end='', flush=True)

def on_click(x, y, button, pressed):
    global recording, frames
    if button == record_key:
        if pressed and not recording:
            recording = True
            frames = []  # Reset frames for new recording
            update_status_display("RECORDING IN PROGRESS...")
        elif not pressed and recording:
            recording = False
            update_status_display("Processing audio...")
            if frames:
                threading.Thread(target=process_audio, args=(frames,)).start()

def process_audio(frames):
    global VOICE_ID
    if not frames:
        update_status_display("No audio frames to process.")
        return

    audio_data = b''.join(frames)
    wav_io = io.BytesIO()

    try:
        with wave.open(wav_io, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(audio_data)
        wav_io.seek(0)
        update_status_display("Processing audio...", 
                            f"Audio data prepared. Size: {len(audio_data)} bytes")
    except Exception as e:
        update_status_display("Error", f"Error preparing audio: {e}")
        return

    try:
        update_status_display("Processing audio...", 
                            "Sending to ElevenLabs for processing...")
        response = client.speech_to_speech.convert_as_stream(
            voice_id=VOICE_ID,
            audio=wav_io,
            output_format="mp3_44100_128",
            model_id="eleven_multilingual_sts_v2"
        )
        
        # Update status display with fresh credit count after processing
        update_status_display("Processing audio...", 
                            "Audio sent. Processing response...")
        
        play_audio(response)
    except Exception as e:
        update_status_display("Error", f"Error processing audio: {e}")

def play_audio(response):
    temp_file = "temp_audio.mp3"
    try:
        with open(temp_file, 'wb') as f:
            for chunk in response:
                f.write(chunk)
        update_status_display("Processing audio...", 
                            "Audio file prepared. Playing...")

        mixer.music.load(temp_file)
        mixer.music.play()
        while mixer.music.get_busy():
            pass
        mixer.music.unload()
        update_status_display("Ready", "Audio playback finished.")
    except Exception as e:
        update_status_display("Error", f"Error playing audio: {e}")
    finally:
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except Exception as e:
                update_status_display("Error", f"Error removing temporary file: {e}")

def capture_audio():
    global frames, stop_flag
    while not stop_flag:
        if recording:
            try:
                data = input_stream.read(FRAMES_PER_BUFFER, exception_on_overflow=False)
                frames.append(data)
            except IOError as e:
                print(f"Error capturing audio: {e}")

def choose_voice():
    global VOICE_ID, current_voice
    clear_console()
    print("\n" + "="*50)
    print("Voice Selection")
    print(get_account_status())
    print("-"*50)
    print("Available voices:")
    for number, (name, _) in voices.items():
        print(f"{number}: {name}")
    print("="*50)
    try:
        choice = int(input("\nEnter the number of the voice you want to use: "))
        if choice in voices:
            current_voice = choice
            VOICE_ID = voices[current_voice][1]
            display_current_settings()
        else:
            print("Invalid choice. Please try again.")
    except ValueError:
        print("Invalid input. Please enter a number.")

def settings_menu():
    global API_KEY
    
    # Try to load existing config first
    if not load_config():
        print("\nWelcome to Voice Changer!")
        print("Before starting, you need to configure your ElevenLabs API key.")
        if not set_api_key():
            print("Failed to configure API key. Please try again.")
            return
        save_config()  # Save the new key to .env
    
    while True:
        display_current_settings()
        print("\nOptions:")
        print("1: Change input device")
        print("2: Change output device")
        print("3: Change recording key")
        print("4: Change voice")
        print("5: Start voice changer")
        print("6: Change API key")
        print("q: Quit")
        choice = input("\nEnter your choice: ")

        if choice == '1':
            select_input_device()
        elif choice == '2':
            select_output_device()
        elif choice == '3':
            select_record_key()
        elif choice == '4':
            choose_voice()
        elif choice == '5':
            if API_KEY is None:
                print("Please configure your API key first.")
            else:
                start_voice_changer()
        elif choice == '6':
            if set_api_key():
                save_config()  # Save the new key if changed
        elif choice == 'q':
            break
        else:
            print("Invalid choice. Please try again.")

def start_voice_changer():
    if API_KEY is None:
        print("Please configure your API key first.")
        return
        
    global input_stream, stop_flag, recording, frames, p
    stop_flag = False
    recording = False
    frames = []
    
    # Reinitialize PyAudio
    p = pyaudio.PyAudio()

    try:
        # Initialize pygame mixer with the specific output device
        if output_device_index is None:
            mixer.init()  # Use system default
        else:
            mixer.init(devicename=p.get_device_info_by_index(output_device_index)['name'])

        # Open input stream with system default if none specified
        input_stream = p.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            input=True,
                            input_device_index=input_device_index,  # None will use system default
                            frames_per_buffer=FRAMES_PER_BUFFER)

        # Initialize mouse listener
        mouse_listener = mouse.Listener(on_click=on_click)
        mouse_listener.start()

        print("\n" + "="*50)
        print("Voice changer is active")
        print(f"Voice: {voices[current_voice][0]}")
        print(f"Press '{record_key}' to record")
        print("="*50)
        print("\nEnter '0' to stop the voice changer or '4' to change the voice: ", end='', flush=True)

        # Start capturing audio in a separate thread
        audio_thread = threading.Thread(target=capture_audio)
        audio_thread.start()

        # Listen for console input
        try:
            while True:
                command = input()
                if command == '0':
                    stop_flag = True
                    print("Stopping voice changer...")
                    break
                elif command == '4':
                    choose_voice()
                    clear_console()
                    print("\n" + "="*50)
                    print("Voice changer is active")
                    print(f"Press '{record_key}' to record")
                    print("="*50)
                    print("\nEnter '0' to stop the voice changer or '4' to change the voice: ", end='', flush=True)
        except KeyboardInterrupt:
            print("\nStopping voice changer...")
            stop_flag = True

        # Wait for the audio thread to finish
        audio_thread.join()

        # Stop and close the streams
        if input_stream.is_active():
            input_stream.stop_stream()
        input_stream.close()
        p.terminate()
        mouse_listener.stop()

    except OSError as e:
        print(f"Error initializing audio devices: {e}")
    finally:
        # Ensure resources are cleaned up even if an error occurs
        try:
            if 'input_stream' in locals():
                if input_stream.is_active():
                    input_stream.stop_stream()
                input_stream.close()
            mixer.quit()
            p.terminate()
            if 'mouse_listener' in locals():
                mouse_listener.stop()
        except Exception as e:
            print(f"Error cleaning up resources: {e}")

if __name__ == "__main__":
    settings_menu()