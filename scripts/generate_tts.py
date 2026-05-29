import asyncio
import json
import os
import random
import whisper
import edge_tts

VOICE = "en-GB-RyanNeural"

async def synthesize(text, voice, output_path):
    communicate = edge_tts.Communicate(text, voice, rate="-5%", pitch="+0Hz")
    await communicate.save(output_path)

def fix_pronunciation(text):
    replacements = {
        "milliseconds": "milli seconds",
        "Milliseconds": "milli seconds",
        "millisecond": "milli second",
        "nanoseconds": "nano seconds",
        "atoms": "ay toms",
        "Atoms": "ay toms",
        "atom": "ay tom",
        "Atom": "ay tom",
        "nucleus": "new klee us",
        "Nucleus": "new klee us",
        "quantum": "kwon tum",
        "Quantum": "kwon tum",
        "neurons": "new rons",
        "Neurons": "new rons",
        "neuron": "new ron",
        "Neuron": "new ron",
        "neuroscience": "new ro science",
        "Neuroscience": "new ro science",
        "neurotransmitter": "new ro transmitter",
        "psychology": "sy col o jee",
        "Psychology": "sy col o jee",
        "psychological": "sy co loj i cal",
        "photons": "foe tons",
        "photon": "foe ton",
        "synapse": "sy naps",
        "synapses": "sy nap ses",
        "dopamine": "doe pa meen",
        "Dopamine": "doe pa meen",
        "serotonin": "ser o toe nin",
        "Serotonin": "ser o toe nin",
        "oxytocin": "ox ee toe sin",
        "amygdala": "a mig da la",
        "Amygdala": "a mig da la",
        "hippocampus": "hip o cam pus",
        "hypothalamus": "hy po thal a mus",
        "mitochondria": "my to con dree a",
        "chromosome": "kro mo some",
        "subconscious": "sub con shus",
        "electromagnetic": "electro magnetic",
        "DNA": "dee en ay",
        "RNA": "ar en ay",
        "IQ": "eye queue",
        "etc": "and so on",
        "vs": "versus",
    }
    for word, replacement in replacements.items():
        text = text.replace(word, replacement)
    return text

def build_text(script):
    all_lines = [script["hook"]] + script["lines"]
    result = " ... ".join(all_lines)
    return result

def generate_tts(script_path="script.json", output_path="narration.mp3"):
    with open(script_path) as f:
        script = json.load(f)
    full_text = build_text(script)
    full_text = fix_pronunciation(full_text)
    print("[INFO] Synthesizing with voice: " + VOICE)
    asyncio.run(synthesize(full_text, VOICE, output_path))
    print("[OK] Narration saved: " + output_path)
    print("[INFO] Running Whisper for word timestamps...")
    model = whisper.load_model("medium")
    result = model.transcribe(output_path, word_timestamps=True, language="en")
    words = []
    for segment in result["segments"]:
        for word in segment.get("words", []):
            w = word["word"].strip()
            if w:
                words.append({
                    "word": w,
                    "start": round(word["start"], 3),
                    "end": round(word["end"], 3)
                })
    with open("timestamps.json", "w") as f:
        json.dump(words, f, indent=2)
    print("[OK] " + str(len(words)) + " word timestamps saved")

if __name__ == "__main__":
    generate_tts()
