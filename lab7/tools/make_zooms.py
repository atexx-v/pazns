import math
import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "results", "screenshots")
OUT = os.path.join(ROOT, "results", "zoom")
FONT = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
RED = (230, 30, 30)
WHITE = (255, 255, 255)
PAD = 20
GAP = 30
MAX_ZOOM = 3.0
MAX_H = 520

FIGURES = {
    "02_qgc_connected": [(0, 0, 300, 56), (1440, 0, 1600, 56)],
    "03_settings_save_path": [(694, 458, 1046, 512)],
    "04_settings_telemetry_logging": [(696, 458, 1090, 612)],
    "05a_inspector_heartbeat": [(410, 112, 760, 228, "R"), (410, 255, 760, 452, "R")],
    "05b_inspector_global_position": [(410, 112, 760, 228, "R"), (410, 255, 850, 545, "R")],
    "05c_inspector_sys_status": [(410, 255, 960, 480, "R")],
    "06_param_wp_spd_edit": [(603, 332, 998, 430, "R")],
    "07_param_wp_spd_saved": [(309, 333, 770, 411, "R")],
    "08_plan_waypoint_position": [(630, 345, 968, 553), (1421, 250, 1598, 482)],
    "08a_plan_overview": [(760, 440, 1260, 570, "B"), (0, 0, 480, 56, "B"), (1421, 130, 1600, 160, "L")],
    "09_mission_start_takeoff": [(0, 0, 260, 56), (1228, 848, 1450, 895)],
    "10_flight_end_landed": [(0, 0, 260, 56), (1208, 845, 1450, 895)],
    "14_logviewer_tlog_replay": [(170, 170, 600, 205, "R"), (438, 505, 800, 775, "R")],
}


def badge(draw, cx, cy, number, font, r=19):
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=RED, outline=WHITE, width=3)
    w = draw.textlength(str(number), font=font)
    draw.text((cx - w / 2, cy - r * 0.8), str(number), font=font, fill=WHITE)


def arrow(draw, start, tip, width=14, head_len=46, head_w=42):
    dx, dy = tip[0] - start[0], tip[1] - start[1]
    length = math.hypot(dx, dy)
    ux, uy = dx / length, dy / length
    nx, ny = -uy, ux
    base = (tip[0] - ux * head_len, tip[1] - uy * head_len)
    pts = [
        (start[0] + nx * width / 2, start[1] + ny * width / 2),
        (base[0] + nx * width / 2, base[1] + ny * width / 2),
        (base[0] + nx * head_w / 2, base[1] + ny * head_w / 2),
        tip,
        (base[0] - nx * head_w / 2, base[1] - ny * head_w / 2),
        (base[0] - nx * width / 2, base[1] - ny * width / 2),
        (start[0] - nx * width / 2, start[1] - ny * width / 2),
    ]
    draw.polygon(pts, fill=RED, outline=WHITE)
    draw.line(pts + [pts[0]], fill=WHITE, width=2)
    draw.polygon(pts, fill=RED)


def arrow_for(box, size, side=None):
    x0, y0, x1, y1 = box[:4]
    w, h = size
    reach = 190
    off = 8
    if side == "R":
        tip = (x1 + off, (y0 + y1) / 2)
        return (min(tip[0] + reach, w - 8), tip[1]), tip
    if side == "B":
        tip = ((x0 + x1) / 2, y1 + off)
        return (tip[0], min(tip[1] + reach, h - 8)), tip
    if side == "L":
        tip = (x0 - off, (y0 + y1) / 2)
        return (max(tip[0] - reach, 8), tip[1]), tip
    if y1 < 120:
        tip = ((x0 + x1) / 2, y1 + off)
        return (tip[0], tip[1] + reach), tip
    if y0 > h - 140:
        tip = ((x0 + x1) / 2, y0 - off)
        return (tip[0], tip[1] - reach), tip
    if x0 > w * 0.62:
        tip = (x0 - off, (y0 + y1) / 2)
        return (tip[0] - reach, tip[1]), tip
    tip = (x0 - off, (y0 + y1) / 2)
    return (max(tip[0] - reach, 8), tip[1]), tip


def compose(name, boxes):
    src = Image.open(os.path.join(SRC, name + ".png")).convert("RGB")
    w, h = src.size
    total_w = 1640
    ow = int(total_w * 0.58)
    k = ow / w
    oh = int(h * k)
    overview = src.resize((ow, oh), Image.LANCZOS)
    col_x = PAD + ow + 24
    col_w = total_w - col_x - PAD // 2
    zooms = []
    for box in boxes:
        bw, bh = box[2] - box[0], box[3] - box[1]
        z = min(MAX_ZOOM, col_w / bw, (oh * 1.2 - 16 * (len(boxes) - 1)) / len(boxes) / bh)
        zooms.append(src.crop(box[:4]).resize((max(1, int(bw * z)), max(1, int(bh * z))), Image.LANCZOS))
    stack_h = sum(c.size[1] for c in zooms) + 16 * (len(zooms) - 1)
    canvas = Image.new("RGB", (total_w, max(oh, stack_h) + 2 * PAD), WHITE)
    canvas.paste(overview, (PAD, PAD))
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.truetype(FONT, 22)
    for i, box in enumerate(boxes, 1):
        rect = [box[0] * k + PAD - 2, box[1] * k + PAD - 2, box[2] * k + PAD + 2, box[3] * k + PAD + 2]
        draw.rectangle(rect, outline=RED, width=3)
        start, tip = arrow_for(box, (w, h), box[4] if len(box) > 4 else None)
        arrow(draw, (start[0] * k + PAD, start[1] * k + PAD), (tip[0] * k + PAD, tip[1] * k + PAD),
              width=9, head_len=30, head_w=28)
        badge(draw, max(rect[0], PAD + 14), max(rect[1], PAD + 14), i, font, 14)
    y = PAD
    for i, crop in enumerate(zooms, 1):
        zw, zh = crop.size
        draw.rectangle((col_x - 3, y - 3, col_x + zw + 3, y + zh + 3), outline=RED, width=3)
        canvas.paste(crop, (col_x, y))
        badge(draw, col_x + 3, y + 3, i, font, 14)
        y += zh + 16
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name + "_zoom.png")
    canvas.save(path, optimize=True)
    return path, canvas.size


for name, boxes in FIGURES.items():
    path, size = compose(name, boxes)
    print("%-36s %dx%d" % (os.path.basename(path), size[0], size[1]))
