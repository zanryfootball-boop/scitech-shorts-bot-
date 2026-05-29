import asyncio
import json
import os
import random
import subprocess
import whisper
import edge_tts

VOICE = "en-GB-RyanNeural"

CONNECTORS = [
    "And here is the fascinating part.",
    "But wait, it gets more interesting.",
    "Now here is what shocked scientists.",
    "And this changes everything.",
    "But most people never know this.",
    "Now here is the mind blowing truth.",
    "And researchers have confirmed this.",
    "But here is what makes it incredible.",
    "Now pay close attention to this.",
    "And this will completely change how you think.",
]

PRONUNCIATION_MAP = {
    "milliseconds": "MIL-ih-sek-undz",
    "Milliseconds": "MIL-ih-sek-undz",
    "millisecond": "MIL-ih-sek-und",
    "Millisecond": "MIL-ih-sek-und",
    "nanoseconds": "NAN-oh-sek-undz",
    "Nanoseconds": "NAN-oh-sek-undz",
    "atoms": "AY-toms",
    "Atoms": "AY-toms",
    "atom": "AY-tom",
    "Atom": "AY-tom",
    "nucleus": "NEW-klee-us",
    "Nucleus": "NEW-klee-us",
    "nuclei": "NEW-klee-eye",
    "quantum": "KWON-tum",
    "Quantum": "KWON-tum",
    "quanta": "KWON-tah",
    "neuron": "NEW-ron",
    "Neuron": "NEW-ron",
    "neurons": "NEW-ronz",
    "Neurons": "NEW-ronz",
    "neuroscience": "NEW-roh-SY-ence",
    "Neuroscience": "NEW-roh-SY-ence",
    "neurotransmitter": "NEW-roh-tranz-MIT-er",
    "Neurotransmitter": "NEW-roh-tranz-MIT-er",
    "psychology": "sy-KOL-oh-jee",
    "Psychology": "sy-KOL-oh-jee",
    "psychological": "sy-koh-LOJ-ih-kul",
    "Psychological": "sy-koh-LOJ-ih-kul",
    "psychologist": "sy-KOL-oh-jist",
    "Psychologist": "sy-KOL-oh-jist",
    "photon": "FOH-ton",
    "Photon": "FOH-ton",
    "photons": "FOH-tonz",
    "Photons": "FOH-tonz",
    "synapse": "SY-naps",
    "Synapse": "SY-naps",
    "synapses": "SY-nap-sez",
    "dopamine": "DOH-pah-meen",
    "Dopamine": "DOH-pah-meen",
    "serotonin": "ser-oh-TOH-nin",
    "Serotonin": "ser-oh-TOH-nin",
    "oxytocin": "ok-see-TOH-sin",
    "Oxytocin": "ok-see-TOH-sin",
    "adrenaline": "ah-DREN-ah-lin",
    "Adrenaline": "ah-DREN-ah-lin",
    "cortisol": "KOR-tih-sol",
    "Cortisol": "KOR-tih-sol",
    "amygdala": "ah-MIG-dah-lah",
    "Amygdala": "ah-MIG-dah-lah",
    "hippocampus": "hip-oh-KAM-pus",
    "Hippocampus": "hip-oh-KAM-pus",
    "hypothalamus": "hy-poh-THAL-ah-mus",
    "Hypothalamus": "hy-poh-THAL-ah-mus",
    "subconscious": "sub-KON-shus",
    "Subconscious": "sub-KON-shus",
    "electromagnetic": "ee-lek-troh-mag-NET-ik",
    "Electromagnetic": "ee-lek-troh-mag-NET-ik",
    "mitochondria": "my-toh-KON-dree-ah",
    "Mitochondria": "my-toh-KON-dree-ah",
    "chromosome": "KROH-moh-sohm",
    "Chromosome": "KROH-moh-sohm",
    "DNA": "dee en ay",
    "RNA": "ar en ay",
    "Hz": "hertz",
    "kHz": "kilo-hertz",
    "MHz": "mega-hertz",
    "GHz": "giga-hertz",
    "km": "kilometers",
    "kg": "kilograms",
    "mg": "milligrams",
    "eg": "for example",
    "ie": "that is",
    "etc": "and so on",
    "vs": "versus",
    "IQ": "eye queue",
}

def fix_pronunciation(text):
    for word, replacement in PRONUNCIATION_MAP.items():
        text = text.replace(word, replacement)
    return text

def build_natural_text(script):
    all_lines = [script["hook"]] + script["lines"]
    result = all_lines[0]
    for i in range(1, len(all_lines)):
        if i % 2 == 0:
            connector = random.choice(CONNECTORS)
            result += " ... " + connector + " ... " + all_lines[i]
        else:
            result += " ... " + all_lines[i]
    return result

async def synthesize(text, voice, output_path):
    communicate = edge_tts.Communicate(text, voice, rate="-18%", pitch="+0Hz", volume="+0%")
    await communicate.save(output_path)

def enhance_audio(input_path, output_path):
    subprocess.run([
        "ffmpeg", "-y", "-i", input_path,
        "-af", "equalizer=f=3000:t=o:w=200:g=3,equalizer=f=200:t=o:w=100:g=-2,acompressor=threshold=-20dB:ratio=4:attack=5:release=50",
        "-ar", "44100",
        output_path
    ], check=True, capture_output=True)
    print("[OK] Audio enhanced")

def generate_tts(script_path="script.json", output_path="narration.mp3"):
    with open(script_path) as f:
        script = json.load(f)

    voice = VOICE
    full_text = build_natural_text(script)
    full_text = fix_pronunciation(full_text)

    print("[INFO] Synthesizing with voice: " + voice)
    raw_audio = output_path.replace(".mp3", "_raw.mp3")
    asyncio.run(synthesize(full_text, voice, raw_audio))
    print("[OK] Raw narration saved")

    print("[INFO] Enhancing audio quality...")
    try:
        enhance_audio(raw_audio, output_path)
        os.remove(raw_audio)
    except Exception as e:
        print("[WARN] Audio enhancement failed, using raw: " + str(e))
        os.rename(raw_audio, output_path)

    print("[INFO] Running Whisper for word timestamps...")
    model = whisper.load_model("small")
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
