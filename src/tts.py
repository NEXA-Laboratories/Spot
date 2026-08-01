import os
import wave
import sounddevice as sd
import soundfile as sf
from piper import PiperVoice


class PiperTTS:
    def __init__(self, config):
        self.config = config["piper_tts"]
        self.temp_output = os.path.abspath("data/output.wav")
        os.makedirs("data", exist_ok=True)

        # Verify absolute paths for your model configuration files
        model_path = os.path.abspath(self.config["model_path"])
        config_path = os.path.abspath(self.config["config_path"])

        print(f"[TTS] Loading native voice profile into RAM: {os.path.basename(model_path)}...")
        try:
            # Native Python API loading pattern
            self.voice = PiperVoice.load(model_path, config_path=config_path, use_cuda=False)
            print("[TTS] Voice module ready.")
        except Exception as e:
            print(f"[TTS Critical Error] Failed to initialize Piper wrapper: {e}")
            print(f"Please verify your config.yaml model paths are correct.")
            self.voice = None

    def speak(self, text: str):
        if not text or not self.voice:
            return

        # Remove markdown characters that trip up pronunciation configurations
        clean_text = text.replace("*", "").replace("_", "").strip()
        print(f"[Amigo Speaking]: {clean_text}")

        try:
            # Generate the local WAV frame using memory blocks natively
            with wave.open(self.temp_output, "wb") as wav_file:
                self.voice.synthesize_wav(clean_text, wav_file)

            # Read and play back instantly over the default sound card device
            if os.path.exists(self.temp_output):
                data, fs = sf.read(self.temp_output)
                sd.play(data, fs)
                sd.wait()  # Pause parent engine execution thread until speech finishes

                # Clean up temporary asset
                os.remove(self.temp_output)

        except Exception as e:
            print(f"[TTS Runtime Error] Direct playback failure: {e}")