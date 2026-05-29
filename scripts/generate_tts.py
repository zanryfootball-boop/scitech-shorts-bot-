import asyncio
import json
import os
import random
import whisper
import edge_tts

VOICES = {
    "deep_space": "en-GB-RyanNeural",
    "neural_blue": "en-GB-RyanNeural",
    "bio_green": "en-GB-RyanNeural",
    "cosmic_purple": "en-GB-RyanNeural",
    "electric_cyan": "en-GB-RyanNeural",
}

CONNECTORS = [
    "And here is the shocking part.",
    "But wait, there is more.",
    "Now listen to this.",
    "And it gets even better.",
    "But that is not all.",
    "Here is what most people do not know.",
    "And scientists have proven this.",
    "Now think about this.",
    "But here is the truth.",
    "And this will blow your mind.",
]

async def synthesize(text, voice, output_path):
    communicate = edge_tts.Communicate(text, voice, rate="-15%", pitch="+0Hz")
    await communicate.save(output_path)

def fix_pronunciation(text):
    text = text.replace("atoms", "AY-toms")
    text = text.replace("Atoms", "AY-toms")
    text = text.replace("atom", "AY-tom")
    text = text.replace("Atom", "AY-tom")
    text = text.replace("nucleus", "NEW-klee-us")
    text = text.replace("Nucleus", "NEW-klee-us")
    text = text.replace("quantum", "KWON-tum")
    text = text.replace("Quantum", "KWON-tum")
    text = text.replace("neuron", "NEW-ron")
    text = text.replace("neurons", "NEW-rons")
    text = text.replace("Neuron", "NEW-ron")
    text = text.replace("Neurons", "NEW-rons")
    text = text.replace("psychology", "sy-KOL-oh-jee")
    text = text.replace("Psychology", "sy-KOL-oh-jee")
    text = text.replace("psychological", "sy-koh-LOJ-ih-kul")
    text = text.replace("Psychological", "sy-koh-LOJ-ih-kul")
    text = text.replace("photon", "FOH-ton")
    text = text.replace("photons", "FOH-tons")
    text = text.replace("Photon", "FOH-ton")
    text = text.replace("Photons", "FOH-tons")
    text = text.replace("neuroscience", "NEW-roh-sy-ence")
    text = text.replace("Neuroscience", "NEW-roh-sy-ence")
    text = text.replace("synapse", "SY-naps")
    text = text.replace("Synapse", "SY-naps")
    text = text.replace("dopamine", "DOH-pah-meen")
    text = text.replace("Dopamine", "DOH-pah-meen")
    text = text.replace("serotonin", "ser-oh-TOH-nin")
    text = text.replace("Serotonin", "ser-oh-TOH-nin")
    return text

def build_natural_text(script):
    all_lines = [script["hook"]] + script["lines"]
    result = all_lines[0]
    for i in range(1, len(all_lines)):
        connector = random.choice(CONNECTORS) if i % 2 == 0 else ""
        if connector:
            result += " ... " + connector + " " + all_lines[i]
        else:
            result += " ... " + all_lines[i]
    return result

def generate_tts(script_path="script.json", output_path="narration.mp3"):
    with open(script_path) as f:
        script = json.load(f)
    voice = VOICES.get(script.get("color_theme", "deep_space"), "en-GB-RyanNeural")
    full_text = build_natural_text(script)
    full_text = fix_pronunciation(full_text)
    print("[INFO] Synthesizing with voice: " + voice)
    asyncio.run(synthesize(full_text, voice, output_path))
    print("[OK] Narration saved: " + output_path)
    print("[INFO] Running Whisper for word timestamps...")
    model = whisper.load_model("base")
    result = model.transcribe(output_path, word_timestamps=True)
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
