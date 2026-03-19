#!/usr/bin/env python3
"""
Generate branded abstract thumbnail backgrounds for SmartWorkStack.
No title text — Blowfish already displays the title on the card.
Creates 1200x630 images with gradient + geometric pattern + small logo.

Usage:
  python3 generate-thumbnail.py --slug "best-ai-writing-tools" --output ./thumb.jpg
  python3 generate-thumbnail.py --slug "notion-vs-obsidian" --category "Comparisons" --output ./thumb.jpg
"""

import argparse
import os
import hashlib
import math
import random
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630

PALETTES = [
    {"bg_top": (12, 68, 124),  "bg_bot": (4, 44, 83),   "accent": (55, 138, 221),  "shapes": (85, 183, 235)},
    {"bg_top": (15, 110, 86),  "bg_bot": (4, 52, 44),    "accent": (93, 202, 165),  "shapes": (29, 158, 117)},
    {"bg_top": (83, 74, 183),  "bg_bot": (38, 33, 92),   "accent": (175, 169, 236), "shapes": (127, 119, 221)},
    {"bg_top": (8, 80, 65),    "bg_bot": (4, 44, 36),    "accent": (29, 158, 117),  "shapes": (93, 202, 165)},
    {"bg_top": (24, 95, 165),  "bg_bot": (2, 30, 58),    "accent": (133, 183, 235), "shapes": (55, 138, 221)},
    {"bg_top": (59, 109, 17),  "bg_bot": (23, 52, 4),    "accent": (151, 196, 89),  "shapes": (99, 153, 34)},
    {"bg_top": (153, 60, 29),  "bg_bot": (74, 27, 12),   "accent": (240, 153, 123), "shapes": (216, 90, 48)},
    {"bg_top": (40, 40, 50),   "bg_bot": (18, 18, 24),   "accent": (133, 183, 235), "shapes": (80, 80, 100)},
]

PATTERNS = ["circles", "grid", "dots", "waves", "hexagons", "diagonal"]


def pick_from_slug(slug, items):
    idx = int(hashlib.md5(slug.encode()).hexdigest(), 16) % len(items)
    return items[idx]


def draw_gradient(img, top, bot):
    d = ImageDraw.Draw(img)
    for y in range(H):
        r = y / H
        c = tuple(int(top[i] * (1 - r) + bot[i] * r) for i in range(3))
        d.line([(0, y), (W, y)], fill=c)


def draw_pattern_circles(d, color, seed):
    rng = random.Random(seed)
    for _ in range(12):
        x = rng.randint(-60, W + 60)
        y = rng.randint(-60, H + 60)
        r = rng.randint(40, 160)
        opacity = rng.randint(15, 40)
        d.ellipse([x - r, y - r, x + r, y + r],
                  outline=(*color, opacity), width=2)
    for _ in range(5):
        x = rng.randint(100, W - 100)
        y = rng.randint(100, H - 100)
        r = rng.randint(20, 60)
        d.ellipse([x - r, y - r, x + r, y + r],
                  fill=(*color, 20))


def draw_pattern_grid(d, color, seed):
    rng = random.Random(seed)
    spacing = rng.randint(60, 100)
    offset_x = rng.randint(0, spacing)
    offset_y = rng.randint(0, spacing)
    for x in range(offset_x, W + spacing, spacing):
        d.line([(x, 0), (x, H)], fill=(*color, 18), width=1)
    for y in range(offset_y, H + spacing, spacing):
        d.line([(0, y), (W, y)], fill=(*color, 18), width=1)
    for x in range(offset_x, W + spacing, spacing):
        for y in range(offset_y, H + spacing, spacing):
            d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(*color, 35))


def draw_pattern_dots(d, color, seed):
    rng = random.Random(seed)
    for _ in range(80):
        x = rng.randint(0, W)
        y = rng.randint(0, H)
        r = rng.randint(2, 8)
        opacity = rng.randint(20, 50)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(*color, opacity))


def draw_pattern_waves(d, color, seed):
    rng = random.Random(seed)
    for wave in range(5):
        y_base = rng.randint(50, H - 50)
        amplitude = rng.randint(20, 60)
        freq = rng.uniform(0.005, 0.015)
        phase = rng.uniform(0, 2 * math.pi)
        opacity = rng.randint(15, 35)
        points = []
        for x in range(0, W, 4):
            y = y_base + int(amplitude * math.sin(freq * x + phase))
            points.append((x, y))
        if len(points) > 1:
            d.line(points, fill=(*color, opacity), width=2)


def draw_pattern_hexagons(d, color, seed):
    rng = random.Random(seed)
    size = rng.randint(40, 70)
    h_dist = size * 1.73
    v_dist = size * 1.5
    for row in range(-1, int(H / v_dist) + 2):
        for col in range(-1, int(W / h_dist) + 2):
            cx = int(col * h_dist + (row % 2) * h_dist / 2)
            cy = int(row * v_dist)
            pts = []
            for i in range(6):
                angle = math.pi / 3 * i + math.pi / 6
                px = cx + int(size * 0.8 * math.cos(angle))
                py = cy + int(size * 0.8 * math.sin(angle))
                pts.append((px, py))
            d.polygon(pts, outline=(*color, 22), fill=None)


def draw_pattern_diagonal(d, color, seed):
    rng = random.Random(seed)
    spacing = rng.randint(40, 80)
    for i in range(-H, W + H, spacing):
        opacity = rng.randint(12, 30)
        d.line([(i, 0), (i + H, H)], fill=(*color, opacity), width=1)


PATTERN_FUNCS = {
    "circles": draw_pattern_circles,
    "grid": draw_pattern_grid,
    "dots": draw_pattern_dots,
    "waves": draw_pattern_waves,
    "hexagons": draw_pattern_hexagons,
    "diagonal": draw_pattern_diagonal,
}


def draw_iso_blocks(d, x, y, scale=1.0):
    s = int(18 * scale)
    h = int(s * 0.577)
    blocks = [
        (x, y, '#85B7EB', '#378ADD', '#185FA5'),
        (x + int(8 * scale), y - int(14 * scale), '#85B7EB', '#378ADD', '#185FA5'),
        (x, y - int(28 * scale), '#97C459', '#639922', '#3B6D11'),
    ]
    for cx, cy, top, left, right in blocks:
        d.polygon([(cx, cy - h), (cx + s, cy), (cx, cy + h), (cx - s, cy)], fill=top)
        d.polygon([(cx - s, cy), (cx, cy + h), (cx, cy + 2 * h), (cx - s, cy + h)], fill=left)
        d.polygon([(cx + s, cy), (cx, cy + h), (cx, cy + 2 * h), (cx + s, cy + h)], fill=right)


def get_font(size, bold=False):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for fp in paths:
        if os.path.exists(fp):
            return ImageFont.truetype(fp, size)
    return ImageFont.load_default()


def generate(slug, output, category=None):
    palette = pick_from_slug(slug, PALETTES)
    pattern_name = pick_from_slug(slug + "_pattern", PATTERNS)
    seed = int(hashlib.md5(slug.encode()).hexdigest(), 16) % 999999

    # Create with alpha for pattern overlay
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw_gradient(img, palette["bg_top"], palette["bg_bot"])

    # Pattern overlay
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    PATTERN_FUNCS[pattern_name](od, palette["shapes"], seed)
    img = Image.alpha_composite(img, overlay)

    d = ImageDraw.Draw(img)

    # Accent bar at top
    d.rectangle([0, 0, W, 4], fill=palette["accent"])

    # Category badge (centered top area — survives cropping)
    if category:
        tag_font = get_font(20, bold=True)
        bbox = d.textbbox((0, 0), category.upper(), font=tag_font)
        tw = bbox[2] - bbox[0]
        pad = 14
        badge_x = (W - tw - 2 * pad) // 2
        d.rounded_rectangle(
            [badge_x, 80, badge_x + tw + 2 * pad, 80 + 36],
            radius=6, fill=(*palette["accent"], 200)
        )
        d.text((badge_x + pad, 86), category.upper(), fill=(255, 255, 255), font=tag_font)

    # Logo + brand (centered bottom — survives cropping)
    logo_x = W // 2 - 60
    draw_iso_blocks(d, logo_x, H - 100, scale=1.2)
    brand_font = get_font(20, bold=True)
    brand_text = "SmartWorkStack"
    bbox = d.textbbox((0, 0), brand_text, font=brand_font)
    bw = bbox[2] - bbox[0]
    d.text((logo_x + 30, H - 116), brand_text, fill=(255, 255, 255, 200), font=brand_font)

    url_font = get_font(14)
    url_text = "smartworkstack.com"
    bbox2 = d.textbbox((0, 0), url_text, font=url_font)
    uw = bbox2[2] - bbox2[0]
    d.text((W // 2 - uw // 2, H - 80), url_text, fill=(255, 255, 255, 120), font=url_font)

    # Save
    os.makedirs(os.path.dirname(output) or ".", exist_ok=True)
    img = img.convert("RGB")
    if output.endswith((".jpg", ".jpeg")):
        img.save(output, "JPEG", quality=90)
    else:
        img.save(output, "PNG")

    size_kb = os.path.getsize(output) // 1024
    print(f"✅ {os.path.basename(output)} ({W}x{H}, {size_kb}KB, {pattern_name})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--slug", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--category", default=None)
    args = parser.parse_args()
    generate(args.slug, args.output, args.category)