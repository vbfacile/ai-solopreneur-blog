#!/usr/bin/env python3
"""
Generate branded thumbnail cards for SmartWorkStack blog articles.
Creates 1200x630 images (Open Graph standard) with:
  - Gradient background matching brand colors
  - Article title (word-wrapped)
  - SmartWorkStack branding
  - Category tag if provided

Usage:
  python3 generate-thumbnail.py --title "Best AI Writing Tools" --slug "best-ai-writing-tools" --output ./thumb.jpg
  python3 generate-thumbnail.py --title "Notion vs Obsidian" --slug "notion-vs-obsidian" --category "Comparisons" --output ./thumb.jpg
"""

import argparse
import os
import hashlib
from PIL import Image, ImageDraw, ImageFont

# ── Brand colors ─────────────────────────────────────────────
PALETTES = [
    # Blue (primary)
    {"bg_top": (12, 68, 124), "bg_bot": (4, 44, 83), "accent": (55, 138, 221)},
    # Blue-green
    {"bg_top": (15, 110, 86), "bg_bot": (4, 52, 44), "accent": (93, 202, 165)},
    # Blue-purple
    {"bg_top": (83, 74, 183), "bg_bot": (38, 33, 92), "accent": (175, 169, 236)},
    # Dark teal
    {"bg_top": (8, 80, 65), "bg_bot": (4, 44, 36), "accent": (29, 158, 117)},
    # Navy
    {"bg_top": (24, 95, 165), "bg_bot": (2, 30, 58), "accent": (133, 183, 235)},
    # Green accent
    {"bg_top": (39, 80, 10), "bg_bot": (23, 52, 4), "accent": (151, 196, 89)},
]

W, H = 1200, 630


def pick_palette(slug):
    """Deterministic palette from slug — same article always gets same color."""
    idx = int(hashlib.md5(slug.encode()).hexdigest(), 16) % len(PALETTES)
    return PALETTES[idx]


def draw_gradient(img, top_color, bot_color):
    """Draw vertical gradient background."""
    d = ImageDraw.Draw(img)
    for y in range(H):
        ratio = y / H
        r = int(top_color[0] * (1 - ratio) + bot_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bot_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bot_color[2] * ratio)
        d.line([(0, y), (W, y)], fill=(r, g, b))


def draw_iso_blocks(d, x, y, scale=1.0):
    """Draw the SmartWorkStack isometric blocks logo."""
    s = int(24 * scale)
    h = int(s * 0.577)

    blocks = [
        # Bottom block (blue)
        (x, y, '#85B7EB', '#378ADD', '#185FA5'),
        # Middle block (blue, offset right)
        (x + int(10 * scale), y - int(18 * scale), '#85B7EB', '#378ADD', '#185FA5'),
        # Top block (green, back left)
        (x, y - int(36 * scale), '#97C459', '#639922', '#3B6D11'),
    ]

    for cx, cy, top, left, right in blocks:
        # Top face
        d.polygon([
            (cx, cy - h), (cx + s, cy), (cx, cy + h), (cx - s, cy)
        ], fill=top)
        # Left face
        d.polygon([
            (cx - s, cy), (cx, cy + h), (cx, cy + 2 * h), (cx - s, cy + h)
        ], fill=left)
        # Right face
        d.polygon([
            (cx + s, cy), (cx, cy + h), (cx, cy + 2 * h), (cx + s, cy + h)
        ], fill=right)


def get_font(size, bold=False):
    """Try to load a nice font, fall back to default."""
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            return ImageFont.truetype(fp, size)
    return ImageFont.load_default()


def wrap_text(text, font, max_width, draw):
    """Word-wrap text to fit within max_width pixels."""
    words = text.split()
    lines = []
    current = ""

    for word in words:
        test = f"{current} {word}".strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def generate(title, slug, output, category=None):
    palette = pick_palette(slug)
    img = Image.new("RGB", (W, H))
    draw_gradient(img, palette["bg_top"], palette["bg_bot"])
    d = ImageDraw.Draw(img)

    # ── Decorative elements ──────────────────────────────────
    # Subtle diagonal lines
    for i in range(0, W + H, 80):
        d.line([(i, 0), (i - H, H)], fill=(*palette["accent"], 15), width=1)

    # Accent bar at top
    d.rectangle([0, 0, W, 6], fill=palette["accent"])

    # ── Category tag (top left) ──────────────────────────────
    margin_x = 80
    tag_y = 50

    if category:
        tag_font = get_font(22, bold=True)
        bbox = d.textbbox((0, 0), category.upper(), font=tag_font)
        tw = bbox[2] - bbox[0]
        padding = 16
        d.rounded_rectangle(
            [margin_x, tag_y, margin_x + tw + 2 * padding, tag_y + 40],
            radius=6, fill=palette["accent"]
        )
        d.text((margin_x + padding, tag_y + 8), category.upper(),
               fill=(255, 255, 255), font=tag_font)
        title_y = tag_y + 60
    else:
        title_y = tag_y + 20

    # ── Title text ───────────────────────────────────────────
    title_font = get_font(52, bold=True)
    max_text_w = W - 2 * margin_x
    lines = wrap_text(title, title_font, max_text_w, d)

    # Limit to 3 lines max
    if len(lines) > 3:
        lines = lines[:3]
        lines[-1] = lines[-1].rstrip() + "..."

    line_height = 66
    for i, line in enumerate(lines):
        d.text((margin_x, title_y + i * line_height), line,
               fill=(255, 255, 255), font=title_font)

    # ── Bottom bar: logo + brand name ────────────────────────
    bottom_y = H - 90
    d.line([(margin_x, bottom_y), (W - margin_x, bottom_y)],
           fill=(*palette["accent"],), width=1)

    # Isometric blocks logo
    draw_iso_blocks(d, margin_x + 30, bottom_y + 50, scale=1.2)

    # Brand name
    brand_font = get_font(26, bold=True)
    d.text((margin_x + 70, bottom_y + 22), "SmartWorkStack",
           fill=(255, 255, 255, 200), font=brand_font)

    # Tagline
    tag_font_small = get_font(16)
    d.text((margin_x + 70, bottom_y + 52), "smartworkstack.com",
           fill=(255, 255, 255, 140), font=tag_font_small)

    # ── Save ─────────────────────────────────────────────────
    os.makedirs(os.path.dirname(output) or ".", exist_ok=True)

    if output.endswith(".jpg") or output.endswith(".jpeg"):
        img = img.convert("RGB")
        img.save(output, "JPEG", quality=90)
    else:
        img.save(output, "PNG")

    size_kb = os.path.getsize(output) // 1024
    print(f"✅ Generated: {output} ({W}x{H}, {size_kb}KB)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate article thumbnail")
    parser.add_argument("--title", required=True, help="Article title")
    parser.add_argument("--slug", required=True, help="Article slug (for color)")
    parser.add_argument("--output", required=True, help="Output file path")
    parser.add_argument("--category", default=None, help="Optional category tag")
    args = parser.parse_args()
    generate(args.title, args.slug, args.output, args.category)
