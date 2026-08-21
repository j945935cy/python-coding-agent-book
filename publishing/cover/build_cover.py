from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math

W, H = 1600, 2400
OUT = Path(__file__).resolve().parent
FONT_CJK = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"


def font(path: str, size: int):
    return ImageFont.truetype(path, size=size)


def fit_text(draw, text, max_width, start_size, path=FONT_CJK, min_size=36):
    size = start_size
    while size >= min_size:
        f = font(path, size)
        box = draw.textbbox((0, 0), text, font=f)
        if box[2] - box[0] <= max_width:
            return f
        size -= 2
    return font(path, min_size)


# Deep editorial background.
img = Image.new("RGB", (W, H), "#06101f")
pix = img.load()
for y in range(H):
    for x in range(W):
        nx, ny = x / W, y / H
        glow = max(0, 1 - math.hypot(nx - 0.76, ny - 0.30) / 0.55)
        glow2 = max(0, 1 - math.hypot(nx - 0.18, ny - 0.78) / 0.48)
        r = int(6 + 8 * glow + 5 * glow2)
        g = int(16 + 34 * glow + 18 * glow2)
        b = int(31 + 45 * glow + 40 * glow2)
        pix[x, y] = (r, g, b)

# Subtle grid.
d = ImageDraw.Draw(img, "RGBA")
for x in range(0, W, 80):
    d.line((x, 0, x, H), fill=(93, 166, 196, 18), width=1)
for y in range(0, H, 80):
    d.line((0, y, W, y), fill=(93, 166, 196, 18), width=1)

# Agent loop artwork: nodes, routes, and a cursor-like signal.
art = Image.new("RGBA", (W, H), (0, 0, 0, 0))
a = ImageDraw.Draw(art, "RGBA")
nodes = [
    (1120, 1080, 132, "MODEL"),
    (1325, 1340, 112, "CALL"),
    (1160, 1630, 122, "TOOL"),
    (835, 1575, 108, "RESULT"),
    (790, 1240, 118, "CTX"),
]
route = [(1120, 1080), (1325, 1340), (1160, 1630), (835, 1575), (790, 1240), (1120, 1080)]
for i in range(len(route) - 1):
    a.line((*route[i], *route[i + 1]), fill=(68, 220, 209, 165), width=9)
for x, y, r, label in nodes:
    a.ellipse((x-r, y-r, x+r, y+r), fill=(8, 27, 48, 238), outline=(86, 229, 216, 235), width=7)
    f = fit_text(a, label, r*1.45, 28, FONT_MONO, 18)
    a.text((x, y), label, font=f, anchor="mm", fill=(205, 255, 248, 245))
# Small data particles.
for i in range(22):
    x = 740 + (i * 71) % 760
    y = 1010 + (i * 113) % 680
    rr = 3 + (i % 4)
    a.ellipse((x-rr, y-rr, x+rr, y+rr), fill=(128, 240, 224, 130))
art = art.filter(ImageFilter.GaussianBlur(0.25))
img = Image.alpha_composite(img.convert("RGBA"), art)
d = ImageDraw.Draw(img, "RGBA")

# Editorial accent and title field.
d.rounded_rectangle((90, 125, 235, 175), radius=20, fill=(59, 226, 206, 245))
d.text((162, 150), ">_", font=font(FONT_MONO, 27), anchor="mm", fill=(4, 25, 40, 255))
d.text((265, 150), "PYTHON × AGENT SYSTEMS", font=font(FONT_MONO, 32), anchor="lm", fill=(170, 235, 236, 230))

title1 = "用 Python 自己寫一個"
f1 = fit_text(d, title1, 1280, 108)
d.text((100, 330), title1, font=f1, fill=(244, 250, 252, 255))

f2 = fit_text(d, "Coding Agent", 1350, 176, FONT_MONO)
d.text((92, 505), "Coding Agent", font=f2, fill=(255, 255, 255, 255))

# Accent underline.
d.rounded_rectangle((100, 720, 660, 742), radius=11, fill=(63, 229, 208, 245))

subtitle_lines = ["從對話迴圈、工具呼叫", "到可擴充的 AI 程式助手"]
for i, line in enumerate(subtitle_lines):
    fs = fit_text(d, line, 1040, 62)
    d.text((105, 835 + i * 92), line, font=fs, fill=(188, 214, 225, 255))

# Bottom identity block.
d.line((100, 2130, 1500, 2130), fill=(160, 201, 214, 95), width=2)
d.text((105, 2195), "Happy eBook Authors", font=font(FONT_CJK, 46), fill=(239, 246, 248, 255))
d.text((1495, 2200), "Happy eBook", font=font(FONT_CJK, 38), anchor="ra", fill=(138, 211, 207, 255))

# Export exact-size RGB assets.
final = img.convert("RGB")
png = OUT / "cover-1600x2400.png"
jpg = OUT / "cover-1600x2400.jpg"
final.save(png, format="PNG", optimize=True)
final.save(jpg, format="JPEG", quality=94, optimize=True, progressive=True)
print(png)
print(jpg)
