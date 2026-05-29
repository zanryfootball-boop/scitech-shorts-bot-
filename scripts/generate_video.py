import json
import math
import os
import random
import subprocess
import tempfile
from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1080, 1920
FPS = 30

COLOR_THEMES = {
    "deep_space":     {"bg": (2, 2, 15),    "accent": (100, 180, 255), "text": (255, 255, 255), "sub": (150, 200, 255), "glow": (50, 100, 255)},
    "neural_blue":    {"bg": (0, 5, 25),    "accent": (0, 150, 255),   "text": (255, 255, 255), "sub": (100, 180, 255), "glow": (0, 100, 255)},
    "bio_green":      {"bg": (0, 10, 5),    "accent": (0, 255, 120),   "text": (255, 255, 255), "sub": (100, 255, 160), "glow": (0, 200, 80)},
    "cosmic_purple":  {"bg": (10, 0, 20),   "accent": (180, 0, 255),   "text": (255, 255, 255), "sub": (200, 100, 255), "glow": (140, 0, 255)},
    "electric_cyan":  {"bg": (0, 10, 15),   "accent": (0, 240, 255),   "text": (255, 255, 255), "sub": (100, 240, 255), "glow": (0, 200, 220)},
}

def get_font(size):
    for path in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    ]:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()

def get_audio_duration(audio_path):
    result = subprocess.run([
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        audio_path
    ], capture_output=True, text=True)
    return float(result.stdout.strip())

def draw_glow_text(draw, text, font, x, y, text_color, glow_color):
    for radius in range(6, 0, -2):
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                if abs(dx) + abs(dy) <= radius:
                    alpha = max(0, 80 - radius * 12)
                    draw.text((x + dx, y + dy), text, font=font, fill=(glow_color[0], glow_color[1], glow_color[2]))
    draw.text((x + 3, y + 3), text, font=font, fill=(0, 0, 0))
    draw.text((x, y), text, font=font, fill=text_color)

def make_neural_network(frame_idx, theme):
    img = Image.new("RGB", (WIDTH, HEIGHT), theme["bg"])
    draw = ImageDraw.Draw(img)
    t = frame_idx / FPS
    rng = random.Random(11)
    nodes = []
    for _ in range(30):
        nx = rng.randint(80, WIDTH - 80)
        ny = rng.randint(80, HEIGHT - 80)
        nodes.append((nx, ny))
    for i, (x1, y1) in enumerate(nodes):
        for j, (x2, y2) in enumerate(nodes):
            if i != j and abs(x1 - x2) < 300 and abs(y1 - y2) < 300:
                pulse = (math.sin(t * 2 + i * 0.5 + j * 0.3) + 1) / 2
                alpha = int(40 * pulse)
                draw.line([(x1, y1), (x2, y2)], fill=(theme["accent"][0], theme["accent"][1], theme["accent"][2]), width=1)
    for i, (nx, ny) in enumerate(nodes):
        pulse = (math.sin(t * 3 + i * 0.7) + 1) / 2
        size = int(8 + 12 * pulse)
        glow_size = size + 10
        draw.ellipse([nx - glow_size, ny - glow_size, nx + glow_size, ny + glow_size],
                     fill=(theme["glow"][0] // 4, theme["glow"][1] // 4, theme["glow"][2] // 4))
        draw.ellipse([nx - size, ny - size, nx + size, ny + size], fill=theme["accent"])
    return img

def make_space_cosmos(frame_idx, theme):
    img = Image.new("RGB", (WIDTH, HEIGHT), (2, 2, 10))
    draw = ImageDraw.Draw(img)
    t = frame_idx / FPS
    rng = random.Random(22)
    for _ in range(300):
        sx = rng.randint(0, WIDTH)
        sy = rng.randint(0, HEIGHT)
        size = rng.uniform(0.5, 3)
        twinkle = (math.sin(t * rng.uniform(0.5, 3) + rng.uniform(0, 6)) + 1) / 2
        brightness = int(150 + 105 * twinkle)
        draw.ellipse([sx - size, sy - size, sx + size, sy + size],
                     fill=(brightness, brightness, min(255, brightness + 50)))
    cx, cy = WIDTH // 2, HEIGHT // 2
    for r in range(400, 0, -20):
        factor = r / 400
        red = int(theme["bg"][0] + (theme["accent"][0] - theme["bg"][0]) * (1 - factor) * 0.3)
        green = int(theme["bg"][1] + (theme["accent"][1] - theme["bg"][1]) * (1 - factor) * 0.3)
        blue = int(theme["bg"][2] + (theme["accent"][2] - theme["bg"][2]) * (1 - factor) * 0.3)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(red, green, blue))
    spiral_arms = 3
    for arm in range(spiral_arms):
        for i in range(100):
            angle = (arm * 2 * math.pi / spiral_arms) + (i * 0.15) + t * 0.2
            radius = 20 + i * 3
            sx = int(cx + radius * math.cos(angle))
            sy = int(cy + radius * math.sin(angle))
            size = max(1, 4 - i // 30)
            if 0 < sx < WIDTH and 0 < sy < HEIGHT:
                draw.ellipse([sx - size, sy - size, sx + size, sy + size], fill=theme["accent"])
    return img

def make_dna_helix(frame_idx, theme):
    img = Image.new("RGB", (WIDTH, HEIGHT), theme["bg"])
    draw = ImageDraw.Draw(img)
    t = frame_idx / FPS
    cx = WIDTH // 2
    for y in range(0, HEIGHT, 8):
        factor = y / HEIGHT
        angle1 = factor * math.pi * 8 + t * 1.5
        angle2 = factor * math.pi * 8 + t * 1.5 + math.pi
        x1 = int(cx + 200 * math.cos(angle1))
        x2 = int(cx + 200 * math.cos(angle2))
        depth1 = (math.sin(angle1) + 1) / 2
        depth2 = (math.sin(angle2) + 1) / 2
        size1 = int(6 + 10 * depth1)
        size2 = int(6 + 10 * depth2)
        color1 = tuple(int(c * (0.4 + 0.6 * depth1)) for c in theme["accent"])
        color2 = tuple(int(c * (0.4 + 0.6 * depth2)) for c in theme["glow"])
        draw.ellipse([x1 - size1, y - size1, x1 + size1, y + size1], fill=color1)
        draw.ellipse([x2 - size2, y - size2, x2 + size2, y + size2], fill=color2)
        if y % 40 == 0:
            draw.line([(x1, y), (x2, y)], fill=(200, 200, 200), width=2)
    return img

def make_atom_particles(frame_idx, theme):
    img = Image.new("RGB", (WIDTH, HEIGHT), theme["bg"])
    draw = ImageDraw.Draw(img)
    t = frame_idx / FPS
    cx, cy = WIDTH // 2, HEIGHT // 2
    orbits = [(250, 1.0, 0), (350, 0.7, math.pi / 3), (450, 0.5, math.pi * 2 / 3)]
    for orbit_r, speed, tilt in orbits:
        for i in range(60):
            angle = i * math.pi / 30
            ex = int(cx + orbit_r * math.cos(angle))
            ey = int(cy + int(orbit_r * 0.4 * math.sin(angle)))
            draw.ellipse([ex - 2, ey - 2, ex + 2, ey + 2],
                         fill=(theme["accent"][0] // 3, theme["accent"][1] // 3, theme["accent"][2] // 3))
        electron_angle = t * speed * 2 + tilt
        ex = int(cx + orbit_r * math.cos(electron_angle))
        ey = int(cy + int(orbit_r * 0.4 * math.sin(electron_angle)))
        for r in range(20, 0, -5):
            glow_alpha = r // 5
            draw.ellipse([ex - r, ey - r, ex + r, ey + r],
                         fill=(theme["glow"][0] // glow_alpha, theme["glow"][1] // glow_alpha, theme["glow"][2] // glow_alpha))
        draw.ellipse([ex - 10, ey - 10, ex + 10, ey + 10], fill=theme["accent"])
    for r in range(40, 0, -8):
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=theme["accent"])
    return img

def make_brain_waves(frame_idx, theme):
    img = Image.new("RGB", (WIDTH, HEIGHT), theme["bg"])
    draw = ImageDraw.Draw(img)
    t = frame_idx / FPS
    rng = random.Random(44)
    for _ in range(20):
        sx = rng.randint(0, WIDTH)
        sy = rng.randint(0, HEIGHT)
        size = rng.uniform(1, 3)
        draw.ellipse([sx - size, sy - size, sx + size, sy + size], fill=(50, 50, 80))
    for wave in range(8):
        pts = []
        amp = 30 + wave * 15
        freq = 0.005 + wave * 0.002
        speed = 1 + wave * 0.3
        phase = wave * math.pi / 4
        y_base = int(HEIGHT * (0.2 + wave * 0.08))
        alpha = 0.3 + wave * 0.08
        color = tuple(int(c * alpha) for c in theme["accent"])
        for x in range(0, WIDTH + 10, 5):
            y = int(y_base + amp * math.sin(freq * x + t * speed + phase))
            pts.append((x, y))
        if len(pts) > 1:
            draw.line(pts, fill=color, width=3)
    cx, cy = WIDTH // 2, int(HEIGHT * 0.5)
    for r in range(200, 0, -25):
        pulse = (math.sin(t * 2 + r * 0.02) + 1) / 2
        alpha = int(30 * pulse * r / 200)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                     fill=(theme["glow"][0] * alpha // 255, theme["glow"][1] * alpha // 255, theme["glow"][2] * alpha // 255))
    return img

def make_galaxy_spiral(frame_idx, theme):
    img = Image.new("RGB", (WIDTH, HEIGHT), (2, 2, 8))
    draw = ImageDraw.Draw(img)
    t = frame_idx / FPS
    rng = random.Random(66)
    for _ in range(200):
        sx = rng.randint(0, WIDTH)
        sy = rng.randint(0, HEIGHT)
        size = rng.uniform(0.5, 2.5)
        brightness = rng.randint(100, 255)
        draw.ellipse([sx - size, sy - size, sx + size, sy + size],
                     fill=(brightness, brightness, min(255, brightness + 40)))
    cx, cy = WIDTH // 2, HEIGHT // 2
    for arm in range(4):
        for i in range(150):
            angle = (arm * math.pi / 2) + (i * 0.12) + t * 0.15
            radius = 15 + i * 4
            px = int(cx + radius * math.cos(angle))
            py = int(cy + radius * math.sin(angle) * 0.6)
            size = max(1, 5 - i // 40)
            alpha = max(0.1, 1 - i / 150)
            color = tuple(int(c * alpha) for c in theme["accent"])
            if 0 < px < WIDTH and 0 < py < HEIGHT:
                draw.ellipse([px - size, py - size, px + size, py + size], fill=color)
    return img

def make_molecule_bonds(frame_idx, theme):
    img = Image.new("RGB", (WIDTH, HEIGHT), theme["bg"])
    draw = ImageDraw.Draw(img)
    t = frame_idx / FPS
    rng = random.Random(33)
    atoms = []
    for i in range(12):
        ax = rng.randint(150, WIDTH - 150)
        ay = rng.randint(150, HEIGHT - 150)
        atoms.append((ax, ay))
    for i, (x1, y1) in enumerate(atoms):
        for j, (x2, y2) in enumerate(atoms):
            if i < j:
                dist = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
                if dist < 400:
                    pulse = (math.sin(t * 2 + i + j) + 1) / 2
                    alpha = int(100 * pulse * (1 - dist / 400))
                    color = tuple(int(c * alpha // 255) for c in theme["accent"])
                    draw.line([(x1, y1), (x2, y2)], fill=color, width=2)
    for i, (ax, ay) in enumerate(atoms):
        pulse = (math.sin(t * 2.5 + i * 0.8) + 1) / 2
        size = int(15 + 20 * pulse)
        for r in range(size + 15, size, -3):
            draw.ellipse([ax - r, ay - r, ax + r, ay + r],
                         fill=(theme["glow"][0] // 6, theme["glow"][1] // 6, theme["glow"][2] // 6))
        draw.ellipse([ax - size, ay - size, ax + size, ay + size], fill=theme["accent"])
    return img

def make_electric_pulses(frame_idx, theme):
    img = Image.new("RGB", (WIDTH, HEIGHT), theme["bg"])
    draw = ImageDraw.Draw(img)
    t = frame_idx / FPS
    rng = random.Random(55)
    for bolt in range(8):
        x = rng.randint(0, WIDTH)
        segments = []
        y = 0
        cx = x
        while y < HEIGHT:
            cx += rng.randint(-60, 60)
            cx = max(50, min(WIDTH - 50, cx))
            y += rng.randint(40, 120)
            segments.append((cx, y))
        active = (math.sin(t * 4 + bolt * 0.8) + 1) / 2
        if active > 0.5:
            alpha = int(200 * active)
            color = (min(255, theme["accent"][0] + 50), min(255, theme["accent"][1] + 50), min(255, theme["accent"][2] + 50))
            prev = (x, 0)
            for seg in segments:
                draw.line([prev, seg], fill=color, width=3)
                prev = seg
    for _ in range(100):
        px = rng.randint(0, WIDTH)
        py = rng.randint(0, HEIGHT)
        size = rng.uniform(1, 5)
        spark = (math.sin(t * rng.uniform(3, 8) + rng.uniform(0, 6)) + 1) / 2
        brightness = int(200 * spark)
        draw.ellipse([px - size, py - size, px + size, py + size],
                     fill=(min(255, brightness + 50), min(255, brightness + 50), brightness))
    return img

BG_MAKERS = {
    "neural_network": make_neural_network,
    "space_cosmos": make_space_cosmos,
    "dna_helix": make_dna_helix,
    "atom_particles": make_atom_particles,
    "brain_waves": make_brain_waves,
    "galaxy_spiral": make_galaxy_spiral,
    "molecule_bonds": make_molecule_bonds,
    "electric_pulses": make_electric_pulses,
}

def get_current_word(timestamps, t):
    for item in timestamps:
        if item["start"] <= t <= item["end"]:
            return item["word"]
    return None

def render_frame(frame_idx, script, theme, timestamps, total_frames, font_word, font_hook, font_small):
    bg_style = script.get("background_style", "neural_network")
    maker = BG_MAKERS.get(bg_style, make_neural_network)
    img = maker(frame_idx, theme)
    draw = ImageDraw.Draw(img)
    t = frame_idx / FPS
    current_word = get_current_word(timestamps, t)
    is_start = t < (timestamps[3]["end"] if len(timestamps) > 3 else 3)
    if current_word:
        font = font_hook if is_start else font_word
        word_upper = current_word.upper()
        w = draw.textlength(word_upper, font=font)
        x = (WIDTH - w) // 2
        y = HEIGHT // 2 - font.size // 2
        pad = 35
        draw.rounded_rectangle(
            [x - pad, y - pad, x + w + pad, y + font.size + pad],
            radius=25, fill=(0, 0, 0)
        )
        draw_glow_text(draw, word_upper, font, x, y, theme["text"], theme["glow"])
    progress = min(t / (total_frames / FPS), 1.0)
    draw.rectangle([0, HEIGHT - 12, WIDTH, HEIGHT], fill=(20, 20, 20))
    draw.rectangle([0, HEIGHT - 12, int(WIDTH * progress), HEIGHT], fill=theme["accent"])
    title = script.get("title", "")[:55]
    tw = draw.textlength(title, font=font_small)
    tx = (WIDTH - tw) // 2
    draw.text((tx + 2, 62), title, font=font_small, fill=(0, 0, 0))
    draw.text((tx, 60), title, font=font_small, fill=theme["sub"])
    return img

def generate_video(script_path="script.json", audio_path="narration.mp3", timestamps_path="timestamps.json", output_path="short.mp4"):
    with open(script_path) as f:
        script = json.load(f)
    with open(timestamps_path) as f:
        timestamps = json.load(f)
    theme = COLOR_THEMES.get(script.get("color_theme", "deep_space"), COLOR_THEMES["deep_space"])
    font_word = get_font(100)
    font_hook = get_font(115)
    font_small = get_font(44)
    audio_duration = get_audio_duration(audio_path)
    print("[INFO] Audio duration: " + str(round(audio_duration, 2)) + "s")
    total_frames = int(audio_duration * FPS) + FPS
    frames_dir = tempfile.mkdtemp()
    print("[INFO] Rendering " + str(total_frames) + " frames...")
    for i in range(total_frames):
        if i % (FPS * 5) == 0:
            print("  Frame " + str(i) + "/" + str(total_frames))
        frame = render_frame(i, script, theme, timestamps, total_frames, font_word, font_hook, font_small)
        frame.save(os.path.join(frames_dir, "frame_{:05d}.png".format(i)))
    video_no_audio = output_path.replace(".mp4", "_noaudio.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-framerate", str(FPS),
        "-i", os.path.join(frames_dir, "frame_%05d.png"),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "23",
        video_no_audio
    ], check=True)
    subprocess.run([
        "ffmpeg", "-y",
        "-i", video_no_audio,
        "-i", audio_path,
        "-c:v", "copy", "-c:a", "aac",
        "-shortest", output_path
    ], check=True)
    os.remove(video_no_audio)
    print("[OK] Video saved: " + output_path)
    return output_path

if __name__ == "__main__":
    generate_video()
