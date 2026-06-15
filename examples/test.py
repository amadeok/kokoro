import loge

from kokoro import KPipeline
import soundfile as sf
import torch
pipelines ={"a": [KPipeline(lang_code="a"), "am_echo"],   
            "j": [KPipeline(lang_code="j"), "jm_kumo"]   }
cur_lan = "a"

#more languages at kokoro.js\src\voices.js
text = '''
私はAIモデルを使って話しています
'''
print(len(text))

import sounddevice as sd
import soundfile as sf
import numpy as np
import pygame
import io
import threading
import pyautogui as pg, pyperclip, time
from pynput import keyboard  # Using pynput for hotkey detection

import pygame
import pygame._sdl2.audio as sdl2_audio

current_sound = None
import queue
q = queue.Queue()

def get_devices(capture_devices: bool = False):
    init_by_me = not pygame.mixer.get_init()
    if init_by_me:
        pygame.mixer.init()
    devices = tuple(sdl2_audio.get_audio_device_names(capture_devices))
    if init_by_me:
        pygame.mixer.quit()
    return devices

def play(file_path: str, device = None):
    if device is None:
        devices = get_devices()
        if not devices:
            raise RuntimeError("No device!")
        device = devices[0]
    print("Play: {}\r\nDevice: {}".format(file_path, device))
    pygame.mixer.init(devicename=device)
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    pygame.mixer.quit()
    
def get_audio_device_index_by_partial(partial_name):
    """Get audio device index by partial name match (case insensitive)."""
    devices = get_devices()
    
    # Search for partial match (case insensitive)
    matches = [(idx, name) for idx, name in enumerate(devices)
               if partial_name.lower() in name.lower()]
    
    if not matches:
        print("No matching audio devices found. Available devices:")
        for idx, name in enumerate(devices):
            print(f"{idx}: {name}")
        return None
    
    # Return first match if multiple found
    if len(matches) > 1:
        print(f"Multiple matches found for '{partial_name}':")
        for idx, name in matches:
            print(f"{idx}: {name}")
    
    return matches[0]

# Initialize audio device
device_index, device_name = get_audio_device_index_by_partial("cable-a")
if device_index is not None:
    print(f"Found matching device at index: {device_index}")
    print(f"Device name: {device_name}")
    pygame.mixer.init(frequency=24000, devicename=device_name)
    print("Audio initialized with selected device")
else:
    print("No matching device found")
stop = False

def generate_and_play_audio():
    global current_sound
    global stop
    while True:
        # Stop any currently playing sound
        data = q.get()
        if 0 and type(data) == int and data == 0:
            if current_sound:
                print("Stopping audio")
                current_sound.stop()
        else:
            print(f"Generating audio")
            buffer = io.BytesIO()
            sf.write(buffer, data, 24000, format='WAV')
            buffer.seek(0)

            pygame.mixer.music.load(buffer)
            pygame.mixer.music.play()
            print(f"Playing audio")
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)  # Sleep briefly to avoid hogging CPU
                # if stop:
                #     stop = False
                #     break
                # stop = False
                
                
def play_clipboard():
    pg.hotkey("control", "c")
    time.sleep(0.01)
    text = pyperclip.paste()
    stop_audio()

    global stop
    # stop = True
    time.sleep(0.01)
    generator = pipelines[cur_lan][0](text, voice= pipelines[cur_lan][1])
    for i, (gs, ps, audio) in enumerate(generator):
        print(i, gs, ps, len(ps))
        q.put(audio)

def stop_audio():
    global stop
    stop = True
    while q.qsize():  q.get()
    # q.put(0)
    if current_sound:
        current_sound.stop()

def on_activate_f8():
    q.put(0)
    
    generator = pipelines[cur_lan][0](text, voice= pipelines[cur_lan][1])
    for i, (gs, ps, audio) in enumerate(generator):
        print(i, gs, ps, len(ps))
        q.put(audio)

def setup_hotkeys():
    # Using pynput's GlobalHotKeys
    with keyboard.GlobalHotKeys({
            '<ctrl>+q': play_clipboard,
            '<ctrl>+<alt>+a': stop_audio,
            '<f8>': on_activate_f8}) as h:
        h.join()

if __name__ == "__main__":
    # Start the audio playback thread
    threading.Thread(target=generate_and_play_audio, daemon=True).start()
    
    # Set up hotkeys
    setup_hotkeys()
    
    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")