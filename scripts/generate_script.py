import json
import random
import os
from datetime import datetime
from groq import Groq

NICHES = [
    "motivational football quotes",
    "football legends motivational speeches",
    "Ronaldo motivational story",
    "Messi never give up story",
    "football motivation for life",
    "football champions mindset",
    "football dedication and hardwork",
    "football dreams and goals",
    "football passion and hunger",
    "football greatness quotes",
]
BACKGROUNDS = [
    "stadium_lights",
    "football_pitch",
    "crowd_energy",
    "goal_celebration",
    "training_ground",
    "trophy_glory",
    "player_silhouette",
    "ball_particles",
]


COLOR_THEMES = {
    "champions_gold":   {"bg": (10, 8, 0),   "accent": (255, 200, 0),   "text": (255, 255, 255), "sub": (255, 220, 80)},
    "pitch_green":      {"bg": (0, 20, 0),   "accent": (0, 220, 80),    "text": (255, 255, 255), "sub": (100, 255, 150)},
    "stadium_night":    {"bg": (5, 5, 20),   "accent": (255, 255, 255), "text": (255, 255, 255), "sub": (200, 200, 255)},
    "fire_red":         {"bg": (20, 0, 0),   "accent": (255, 50, 0),    "text": (255, 255, 255), "sub": (255, 120, 60)},
    "royal_blue":       {"bg": (0, 5, 30),   "accent": (0, 100, 255),   "text": (255, 255, 255), "sub": (100, 180, 255)},
}

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
        '  "description": "YouTube description (2-3 sentences) end with these exact hashtags: ' + hashtags + ' #shorts",\n'
        '  "tags": ["shorts", "youtubeshorts"],\n'
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
