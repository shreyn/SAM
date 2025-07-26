"""
Vosk-based local Speech-to-Text (STT) for SAM v5

Instructions:
- Install dependencies: pip install vosk sounddevice
- Download a Vosk English model from https://alphacephei.com/vosk/models
  (e.g., 'vosk-model-en-us-0.22' or any compatible version)
- Unzip the model to 'v5/STT/models/vosk-model-en-us-0.22'

Usage:
from v5.STT.vosk_stt import VoskSTT
stt = VoskSTT()
text = stt.listen_and_transcribe()
"""
import os
import queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer

class VoskSTT:
    def __init__(self, model_path=None, samplerate=16000):
        if model_path is None:
            # Default model path (update to match the actual model you have)
            model_path = os.path.join(os.path.dirname(__file__), 'models', 'vosk-model-en-us-0.22')
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Vosk model not found at {model_path}. Download and unzip a model as per the instructions.")
        self.model = Model(model_path)
        self.samplerate = samplerate
        self.q = queue.Queue()

    def _callback(self, indata, frames, time, status):
        self.q.put(bytes(indata))

    def listen_and_transcribe(self, prompt="[STT] Speak now (press Ctrl+C to stop): "):
        print(prompt)
        with sd.RawInputStream(samplerate=self.samplerate, blocksize=8000, dtype='int16', channels=1, callback=self._callback):
            rec = KaldiRecognizer(self.model, self.samplerate)
            result_text = ""
            try:
                while True:
                    data = self.q.get()
                    if rec.AcceptWaveform(data):
                        res = rec.Result()
                        import json
                        text = json.loads(res).get('text', '')
                        if text:
                            print(f"[STT] Final: {text}")
                            result_text += text + " "
                            break  # For single utterance, break after first result
                    else:
                        partial = rec.PartialResult()
                        import json
                        partial_text = json.loads(partial).get('partial', '')
                        if partial_text and partial_text.lower() not in {"the", ""} and len(partial_text) > 2:
                            print(f"[STT] Partial: {partial_text}", end='\r')
            except KeyboardInterrupt:
                print("\n[STT] Stopped listening.")
            return result_text.strip()

if __name__ == "__main__":
    print("[STT TEST] Testing VoskSTT module...")
    stt = VoskSTT()
    
    try:
        text = stt.listen_and_transcribe()
        print(f"[STT TEST] Recognized: {text}")
    except Exception as e:
        print(f"[STT TEST] Error: {e}") 