import pyaudio
import numpy as np
from faster_whisper import WhisperModel
import io
import wave


class AudioInputEngine:
    def __init__(self, config):
        self.config = config["system"]

        # Initialize ultra-fast, local offline Whisper engine
        # "tiny.en" is tiny, fast, and highly accurate for English smart speakers
        print("[Audio] Loading local Whisper model weights...")
        self.model = WhisperModel("small.en", device="cpu", compute_type="int8")

        # Audio stream pipeline settings
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        self.CHUNK = 1024
        self.p = pyaudio.PyAudio()

        # Simple energy thresholding variables
        self.THRESHOLD = 500  # Adjust up or down depending on room noise
        self.SILENCE_LIMIT = 1.5  # Seconds of silence before stopping recording

    def listen_for_command(self) -> str:
        stream = self.p.open(format=self.FORMAT, channels=self.CHANNELS,
                             rate=self.RATE, input=True,
                             frames_per_buffer=self.CHUNK)

        print("\n[Audio] Listening...")
        frames = []
        recording = False
        silent_chunks = 0
        max_silent_chunks = int(self.SILENCE_LIMIT * self.RATE / self.CHUNK)

        while True:
            try:
                data = stream.read(self.CHUNK, exception_on_overflow=False)
                audio_data = np.frombuffer(data, dtype=np.int16)
                amplitude = np.max(np.abs(audio_data))

                if amplitude > self.THRESHOLD:
                    if not recording:
                        print("[Audio] Voice activity detected, recording phrase...")
                        recording = True
                    frames.append(data)
                    silent_chunks = 0  # Reset silence timer
                elif recording:
                    frames.append(data)
                    silent_chunks += 1
                    if silent_chunks > max_silent_chunks:
                        # Finished speaking
                        break
                else:
                    # Keep a tiny buffer of pre-trigger audio so words aren't cut off
                    pass

            except IOError:
                continue

        # Close stream safely
        stream.stop_stream()
        stream.close()

        if not frames:
            return ""

        # Convert recorded PCM chunks into an in-memory WAV file for Whisper
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wf:
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
            wf.setframerate(self.RATE)
            wf.writeframes(b''.join(frames))

        wav_buffer.seek(0)

        # Transcribe locally completely offline
        print("[Audio] Synthesizing speech locally...")
        segments, _ = self.model.transcribe(wav_buffer, beam_size=1)
        text = "".join([segment.text for segment in segments])

        return text.strip()