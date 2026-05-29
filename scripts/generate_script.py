import json
import random
import os
from datetime import datetime
from groq import Groq

NICHES = [
    "mind blowing psychology facts",
    "dark psychology facts nobody tells you",
    "science facts that sound completely fake",
    "human brain facts that will shock you",
    "quantum physics explained simply",
    "psychology of human behavior",
    "space science facts that blow your mind",
    "science behind human emotions",
    "psychology tricks used on you daily",
    "biology facts about the human body",
    "science facts about the universe",
    "psychology of success and mindset",
    "neuroscience facts about the brain",
    "science facts about black holes",
    "psychology behind social media addiction",
]

BACKGROUNDS = [
    "neural_network",
    "space_cosmos",
    "dna_helix",
    "atom_particles",
    "brain_waves",
    "galaxy_spiral",
    "molecule_bonds",
    "electric_pulses",
]

COLOR_THEMES = [
    "deep_space",
    "neural_blue",
    "bio_green",
    "cosmic_purple",
    "electric_cyan",
]

def generate_script():
    api_key = "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"
    client = Groq(api_key=api_key)
    niche = random.choice(NICHES)
    background = random.choice(BACKGROUNDS)
    color_theme = random.choice(COLOR_THEMES)
    slot = "morning" if datetime.now().hour < 12 else "evening"
    prompt = (
        "You are a viral YouTube Shorts script writer specializing in science and psychology facts. "
        "Write a 60-second mind-blowing script for a Short about: " + niche + "\n\n"
        "The video is for the " + slot + " audience.\n\n"
        "Rules:\n"
        "- Start with a shocking hook that makes people stop scrolling\n"
        "- Use simple language anyone can understand\n"
        "- Each line must be short and punchy (max 10 words)\n"
        "- Include one shocking statistic or fact\n"
        "- End with a call to action\n\n"
        "Return ONLY valid JSON with this exact structure:\n"
        "{\n"
        '  "title": "YouTube title (max 70 chars, curiosity-driven)",\n'
        '  "description": "YouTube description (2-3 sentences + hashtags like #psychology #science #facts #shorts)",\n'
        '  "tags": ["psychology", "science", "facts", "shorts", "mindblown"],\n'
        '  "hook": "First 3 seconds hook line (shocking, makes people stop scrolling)",\n'
        '  "lines": [\n'
        '    "Line 1 (short, shocking fact)",\n'
        '    "Line 2",\n'
        '    "Line 3",\n'
        '    "Line 4",\n'
        '    "Line 5",\n'
        '    "Line 6",\n'
        '    "Line 7 - powerful closing + follow for more"\n'
        '  ],\n'
        '  "background_style": "' + background + '",\n'
        '  "color_theme": "' + color_theme + '"\n'
        "}"
    )
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
        temperature=0.9,
    )
    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()
    script = json.loads(raw)
    script["niche"] = niche
    script["generated_at"] = datetime.utcnow().isoformat()
    with open("script.json", "w") as f:
        json.dump(script, f, indent=2)
    print("[OK] Script generated: " + script["title"])
    return script

if __name__ == "__main__":
    generate_script()
