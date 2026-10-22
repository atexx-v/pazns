import csv
import datetime
import math
import os

import xlsxwriter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(ROOT, "results", "telemetry", "2026-10-21 21-41-37 vehicle1.csv")
OUT = os.path.join(ROOT, "lab7_analysis_vishnevskiy_ir33.xlsx")
EPOCH = datetime.datetime(1899, 12, 30)
SHEET = "Аналіз"
FIRST = 5


def read_env(path):
    values = {}
    for line in open(path, encoding="utf-8"):
        line = line.split("#", 1)[0].strip()
        if "=" in line and "$" not in line:
            key, val = line.split("=", 1)
            values[key] = val
    return values


def hms(text):
    h, m, s = (int(x) for x in text.split(":"))
    return h * 3600 + m * 60 + s


def serial(dt):
    return (dt - EPOCH).total_seconds() / 86400


def haversine(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2
    return 2 * 6371000 * math.asin(math.sqrt(a))


def to_cell(value):
    try:
        return float(value)
    except ValueError:
        return value


env = read_env(os.path.join(ROOT, "variant.env"))
H, V = float(env["ALT_M"]), float(env["SPEED_MS"])
LAT_T, LON_T = float(env["TARGET_LAT"]), float(env["TARGET_LON"])

with open(CSV_PATH, encoding="utf-8") as f:
    raw = list(csv.reader(f))
header, body = raw[0], raw[1:]
col = {name: i for i, name in enumerate(header)}

stamps = [datetime.datetime.strptime(r[col["Timestamp"]], "%Y-%m-%d %H:%M:%S.%f") for r in body]
fsec = [hms(r[col["flightTime"]]) for r in body]
alt_all = [float(r[col["altitudeRelative"]]) for r in body]

i0 = 0
for i in range(1, len(body)):
    if fsec[i] < fsec[i - 1]:
        i0 = i
peak = max(range(i0, len(body)), key=lambda i: alt_all[i])
final_f = max(fsec[i0:])
i_last = next(i for i in range(peak, len(body)) if fsec[i] == final_f)
N = i_last - i0 + 1
LAST = FIRST + N - 1


def num(name, k):
    return float(body[i0 + k][col[name]])


t_s = [(stamps[i0 + k] - stamps[i0]).total_seconds() for k in range(N)]
alt = [num("altitudeRelative", k) for k in range(N)]
gs = [num("groundSpeed", k) for k in range(N)]
asp = [num("airSpeed", k) for k in range(N)]
roll = [num("roll", k) for k in range(N)]
lat = [num("gps.lat", k) for k in range(N)]
lon = [num("gps.lon", k) for k in range(N)]
t_take = min(t_s[k] for k in range(N) if alt[k] >= 0.99 * H)
cruise = [t_s[k] for k in range(N) if gs[k] >= 0.5 and alt[k] >= 0.95 * H]
t_c0, t_c1, t_end = min(cruise), max(cruise) + 1, max(t_s)

wb = xlsxwriter.Workbook(OUT)
GRID = "#BFBFBF"
base = {"font_name": "Arial", "font_size": 11, "valign": "vcenter"}


def fmt(**kw):
    return wb.add_format(dict(base, **kw))


fm = {
    "title": fmt(bold=True, font_size=16),
    "sub": fmt(font_color="#404040"),
    "section": fmt(bold=True, font_size=12, bottom=1),
    "head": fmt(bold=True, bg_color="#D9D9D9", border=1, border_color=GRID),
    "head_c": fmt(bold=True, bg_color="#D9D9D9", border=1, border_color=GRID, align="center"),
    "label": fmt(border=1, border_color=GRID),
    "src": fmt(border=1, border_color=GRID, font_color="#404040"),
    "txt_c": fmt(border=1, border_color=GRID, align="center"),
    "n0": fmt(border=1, border_color=GRID, align="center", num_format="0"),
    "n1": fmt(border=1, border_color=GRID, align="center", num_format="0.0"),
    "n2": fmt(border=1, border_color=GRID, align="center", num_format="0.00"),
    "n7": fmt(border=1, border_color=GRID, align="center", num_format="0.0000000"),
    "time": fmt(border=1, border_color=GRID, align="center", num_format="hh:mm:ss"),
    "d_dt": fmt(border=1, border_color=GRID, num_format="yyyy-mm-dd hh:mm:ss.000"),
    "d_tm": fmt(border=1, border_color=GRID, align="center", num_format="[h]:mm:ss"),
    "d_i": fmt(border=1, border_color=GRID, align="center", num_format="0"),
    "d_1": fmt(border=1, border_color=GRID, align="center", num_format="0.0"),
    "d_2": fmt(border=1, border_color=GRID, align="center", num_format="0.00"),
    "d_7": fmt(border=1, border_color=GRID, align="center", num_format="0.0000000"),
    "d_t": fmt(border=1, border_color=GRID),
    "plain": fmt(),
    "note": fmt(text_wrap=True, valign="top"),
    "note_b": fmt(bold=True, text_wrap=True, valign="top"),
}

ws = wb.add_worksheet(SHEET)
wn = wb.add_worksheet("Примітки")
wc = wb.add_worksheet("CSV")
ws.hide_gridlines(2)
wn.hide_gridlines(2)

bold = wb.add_format({"bold": True})
stamp_fmt = wb.add_format({"num_format": "yyyy-mm-dd hh:mm:ss.000"})
for j, name in enumerate(header):
    wc.write(0, j, name, bold)
for i, row in enumerate(body):
    for j, value in enumerate(row):
        if j == col["Timestamp"]:
            wc.write_datetime(i + 1, j, stamps[i], stamp_fmt)
        else:
            cell = to_cell(value)
            if isinstance(cell, float):
                wc.write_number(i + 1, j, cell)
            else:
                wc.write_string(i + 1, j, cell)
wc.freeze_panes(1, 1)
wc.set_column(col["Timestamp"], col["Timestamp"], 24)

widths = {"A": 46, "B": 30, "C": 12, "D": 74, "E": 3,
          "F": 10, "G": 24, "H": 12, "I": 20, "J": 17, "K": 14, "L": 11, "M": 13, "N": 13, "O": 15,
          "P": 18, "Q": 18, "R": 8, "S": 18, "T": 18, "U": 22, "V": 3, "W": 10, "X": 10, "Y": 42}
for letter, w in widths.items():
    ws.set_column("%s:%s" % (letter, letter), w)


def R(c):
    return "$%s$%d:$%s$%d" % (c, FIRST, c, LAST)


ws.write("A1", "Лабораторна робота №7, варіант 5. Аналіз телеметрії QGroundControl", fm["title"])
ws.write("A2", "Дані польоту – у стовпцях F:U, вихідний файл QGroundControl – на аркуші «CSV», пояснення вибору колонки часу – на аркуші «Примітки».", fm["sub"])


def section(row, text):
    ws.merge_range(row - 1, 0, row - 1, 3, text, fm["section"])


def table_head(row, labels):
    for j, text in enumerate(labels):
        ws.write(row - 1, j, text, fm["head"] if j in (0, 3) else fm["head_c"])


section(4, "Параметри варіанта")
table_head(5, ["Параметр", "Значення", "Одиниця", "Джерело значення"])
params = [
    (6, "Висота зльоту H", H, "м", "n1", "Таблиця 7.6 методички, варіант 5"),
    (7, "Горизонтальна швидкість V", V, "м/с", "n1", "Таблиця 7.6 методички, варіант 5"),
    (8, "Цільова точка, широта", LAT_T, "°", "n7", "Таблиця 7.6 методички, варіант 5"),
    (9, "Цільова точка, довгота", LON_T, "°", "n7", "Таблиця 7.6 методички, варіант 5"),
]
for r, label, val, unit, nf, source in params:
    ws.write(r - 1, 0, label, fm["label"])
    ws.write_number(r - 1, 1, val, fm[nf])
    ws.write(r - 1, 2, unit, fm["txt_c"])
    ws.write(r - 1, 3, source, fm["src"])
ws.write(9, 0, "WPNAV_SPEED = 100 · V", fm["label"])
ws.write_formula(9, 1, "=100*B7", fm["n0"], 100 * V)
ws.write(9, 2, "см/с", fm["txt_c"])
ws.write(9, 3, "Формула методички; у ArduCopter V4.8.0-dev такого параметра немає", fm["src"])
ws.write(10, 0, "WP_SPD (замінник WPNAV_SPEED)", fm["label"])
ws.write_formula(10, 1, "=B7", fm["n1"], V)
ws.write(10, 2, "м/с", fm["txt_c"])
ws.write(10, 3, "Параметр, який задано в QGroundControl", fm["src"])

section(13, "Межі етапів польоту")
table_head(14, ["Етап", "Час від початку польоту", "Одиниця", "Як визначено"])
bounds = [
    (15, "Кінець зльоту", "=MIN(%s)" % R("S"), t_take, "перший момент, коли altitudeRelative ≥ 0,99·H"),
    (16, "Початок горизонтального польоту", "=MIN(%s)" % R("T"), t_c0, "groundSpeed ≥ 0,5 м/с на висоті ≥ 0,95·H"),
    (17, "Кінець горизонтального польоту", "=MAX(%s)+1" % R("T"), t_c1, "остання секунда з groundSpeed ≥ 0,5 м/с на висоті"),
    (18, "Кінець польоту (disarm)", "=MAX(%s)" % R("R"), t_end, "остання секунда польоту, flightTime припиняє зростати"),
]
for r, label, formula, val, how in bounds:
    ws.write(r - 1, 0, label, fm["label"])
    ws.write_formula(r - 1, 1, formula, fm["n1"], val)
    ws.write(r - 1, 2, "с", fm["txt_c"])
    ws.write(r - 1, 3, how, fm["src"])

section(20, "Таблиця 7.4 – Результати аналізу телеметрії")
table_head(21, ["Показник", "Значення", "Одиниця", "Джерело значення (стовпець CSV або повідомлення MAVLink)"])
err = haversine(lat[-1], lon[-1], LAT_T, LON_T)
rows74 = [
    ("Час зльоту (arm, початок набору висоти)", "=G%d" % FIRST, serial(stamps[i0]), "time", "UTC", "Timestamp, перший рядок польоту"),
    ("Тривалість набору висоти H", "=B15", t_take, "n0", "с", "Timestamp, altitudeRelative ≥ 0,99·H"),
    ("Найбільша висота", "=MAX(%s)" % R("I"), max(alt), "n1", "м", "altitudeRelative"),
    ("Найбільша швидкість (наземна)", "=MAX(%s)" % R("J"), max(gs), "n1", "м/с", "groundSpeed"),
    ("Найбільша швидкість (повітряна)", "=MAX(%s)" % R("K"), max(asp), "n1", "м/с", "airSpeed (оцінка автопілота)"),
    ("Час польоту", "=ROUND(H%d*86400,0)" % LAST, final_f, "n0", "с", "flightTime (лічильник QGroundControl, останнє значення)"),
    ("Початкова координата", None,
     "%.7f; %.7f" % (lat[0], lon[0]), "txt_c", "°", "gps.lat, gps.lon (перший рядок польоту, клітинки M5 і N5)"),
    ("Кінцева координата", None,
     "%.7f; %.7f" % (lat[-1], lon[-1]), "txt_c", "°", "gps.lat, gps.lon (останній рядок польоту, клітинки M%d і N%d)" % (LAST, LAST)),
    ("Максимальний roll", "=MAX(MAX(%s),-MIN(%s))" % (R("L"), R("L")), max(max(roll), -min(roll)), "n1", "град", "roll"),
]
for i, (label, formula, val, nf, unit, source) in enumerate(rows74):
    r = 21 + i
    ws.write(r, 0, label, fm["label"])
    if formula is None:
        ws.write_string(r, 1, val, fm[nf])
    else:
        ws.write_formula(r, 1, formula, fm[nf], val)
    ws.write(r, 2, unit, fm["txt_c"])
    ws.write(r, 3, source, fm["src"])
r = 21 + len(rows74)
ws.write(r, 0, "Режими польоту", fm["label"])
ws.write(r, 1, "Stabilize → Guided → Auto", fm["txt_c"])
ws.write(r, 2, "", fm["txt_c"])
ws.write(r, 3, ".tlog: HEARTBEAT, custom_mode (0 → 4 → 3); у CSV такого стовпця немає", fm["src"])
ws.write(r + 1, 0, "Стан arm до та після місії", fm["label"])
ws.write(r + 1, 1, "disarmed → armed → disarmed", fm["txt_c"])
ws.write(r + 1, 2, "", fm["txt_c"])
ws.write(r + 1, 3, ".tlog: HEARTBEAT, base_mode, біт 128 (armed)", fm["src"])

c0 = r + 4
section(c0, "Порівняння заданого з фактичним")
table_head(c0 + 1, ["Параметр", "Задано", "Фактично", "Відхилення"])
hv = ("2*6371000*ASIN(SQRT(SIN(RADIANS(M%d-B8)/2)^2+COS(RADIANS(B8))*COS(RADIANS(M%d))*SIN(RADIANS(N%d-B9)/2)^2))"
      % (LAST, LAST, LAST))
cmp_rows = [
    ("Висота, м", "=B6", H, "=B24", max(alt)),
    ("Швидкість, м/с", "=B7", V, "=B25", max(gs)),
    ("Відстань до цільової точки, м", "=0", 0.0, "=" + hv, err),
]
for i, (label, f_set, v_set, f_fact, v_fact) in enumerate(cmp_rows):
    rr = c0 + 1 + i
    ws.write(rr, 0, label, fm["label"])
    ws.write_formula(rr, 1, f_set, fm["n2"], v_set)
    ws.write_formula(rr, 2, f_fact, fm["n2"], v_fact)
    ws.write_formula(rr, 3, "=C%d-B%d" % (rr + 1, rr + 1), fm["n2"], v_fact - v_set)
dh, fd = float(body[i_last][col["distanceToHome"]]), float(body[i_last][col["flightDistance"]])
rr = c0 + 4
for i, (label, ref, val) in enumerate([("Відстань від точки старту до цілі, м", "=P%d" % LAST, dh),
                                        ("Пройдена відстань за flightDistance, м", "=Q%d" % LAST, fd)]):
    ws.write(rr + i, 0, label, fm["label"])
    ws.write(rr + i, 1, "–", fm["txt_c"])
    ws.write_formula(rr + i, 2, ref, fm["n1"], val)
    ws.write(rr + i, 3, "–", fm["txt_c"])
chart_row = rr + 4

dheads = ["Рядок CSV", "Timestamp", "flightTime", "altitudeRelative, м", "groundSpeed, м/с", "airSpeed, м/с", "roll, град",
          "gps.lat", "gps.lon", "climbRate, м/с", "distanceToHome, м", "flightDistance, м", "t, с",
          "t: висота ≥ 0,99·H", "t: горизонтальний", "Етап польоту"]
ws.merge_range(2, 5, 2, 20, "Дані польоту (значення скопійовано з аркуша «CSV», рядки %d–%d)" % (i0 + 2, i_last + 2), fm["section"])
for j, text in enumerate(dheads):
    ws.write(3, 5 + j, text, fm["head_c"])

data_cols = [("altitudeRelative", "I", "d_1"), ("groundSpeed", "J", "d_1"), ("airSpeed", "K", "d_1"), ("roll", "L", "d_2"),
             ("gps.lat", "M", "d_7"), ("gps.lon", "N", "d_7"), ("climbRate", "O", "d_1"),
             ("distanceToHome", "P", "d_1"), ("flightDistance", "Q", "d_1")]
for k in range(N):
    row = FIRST - 1 + k
    n = FIRST + k
    ws.write_number(row, 5, i0 + k + 2, fm["d_i"])
    ws.write_datetime(row, 6, stamps[i0 + k], fm["d_dt"])
    ws.write_number(row, 7, fsec[i0 + k] / 86400, fm["d_tm"])
    for name, letter, nf in data_cols:
        ws.write_number(row, ord(letter) - ord("A"), num(name, k), fm[nf])
    ws.write_formula(row, 17, "=(G%d-$G$%d)*86400" % (n, FIRST), fm["d_1"], t_s[k])
    up = alt[k] >= 0.99 * H
    ws.write_formula(row, 18, '=IF(I%d>=0.99*$B$6,R%d,"")' % (n, n), fm["d_1"], t_s[k] if up else "")
    in_c = gs[k] >= 0.5 and alt[k] >= 0.95 * H
    ws.write_formula(row, 19, '=IF(AND(J%d>=0.5,I%d>=0.95*$B$6),R%d,"")' % (n, n, n), fm["d_1"], t_s[k] if in_c else "")
    tk = t_s[k]
    stage = "Зліт" if tk <= t_take else ("Перехід" if tk < t_c0 else ("Горизонтальний політ" if tk < t_c1 else "Посадка"))
    ws.write_formula(row, 20, '=IF(R%d<=$B$15,"Зліт",IF(R%d<$B$16,"Перехід",IF(R%d<$B$17,"Горизонтальний політ","Посадка")))' % (n, n, n),
                     fm["d_t"], stage)

PLOTS = os.path.join(ROOT, "results", "analysis")
for i, (png, title) in enumerate([("plot_altitude.png", "Висота від часу"),
                                  ("plot_airspeed.png", "Повітряна швидкість від часу"),
                                  ("plot_groundspeed.png", "Наземна швидкість від часу")]):
    top = chart_row + i * 19
    ws.write(top - 1, 0, title, fm["section"])
    ws.insert_image(top, 0, os.path.join(PLOTS, png), {"x_scale": 0.95, "y_scale": 0.95, "object_position": 2})

ws.set_landscape()
ws.set_paper(9)
ws.print_area(0, 0, chart_row + 58, 3)
ws.fit_to_pages(1, 0)
ws.activate()

wn.set_column("A:A", 130)
wn.write("A1", "Примітки до розрахунку", fm["title"])
notes = [
    ("Звідки значення", "Усі показники таблиці 7.4 обчислено формулами за стовпцями аркуша «Аналіз» (F:U). Значення цих стовпців скопійовано з "
     "аркуша «CSV» (вихідний файл QGroundControl) без змін, номер рядка CSV вказано в стовпці F. Для кожного показника в таблиці 7.4 "
     "є колонка «Джерело значення»."),
    ("Яку колонку часу взято", "У CSV є кілька стовпців, пов'язаних із часом: Timestamp (час запису рядка, безперервний ряд із дробовою секундою), "
     "flightTime (лічильник польоту QGroundControl у форматі год:хв:с, крок 1 с, скидається при кожному arm і зупиняється після disarm), "
     "clock.currentTime і clock.currentUTCTime (годинник апарата), hobbs, timeToHome (оцінка часу повернення). Вісь часу на графіках "
     "t = Timestamp − Timestamp першого рядка польоту; «Час польоту» у таблиці 7.4 взято зі стовпця flightTime."),
    ("Як виділено політ", "CSV QGroundControl пишеться безперервно з моменту підключення, тому містить рядки до і після польоту. "
     "Початок польоту – останнє скидання flightTime (початок останнього arm), кінець – рядок, у якому flightTime зупиняється після disarm. "
     "Етапи визначено за даними: зліт – до досягнення 99 % заданої висоти, горизонтальний політ – поки groundSpeed ≥ 0,5 м/с на висоті не нижче "
     "95 % заданої, посадка – від зупинки над ціллю до дотику."),
    ("Повітряна швидкість", "ArduCopter без датчика швидкості повітря дає в airSpeed оцінку автопілота. У симуляції немає вітру, "
     "тому вона майже збігається з groundSpeed."),
    ("Режими і стан arm", "У CSV QGroundControl немає режиму польоту й стану arm. Ці показники взято з журналу .tlog: повідомлення HEARTBEAT "
     "(custom_mode: 0 – Stabilize, 4 – Guided, 3 – Auto; base_mode, біт 128 – armed)."),
    ("Швидкість у параметрі автопілота", "За методичкою WPNAV_SPEED = 100 · V (см/с). У ArduCopter V4.8.0-dev такого параметра немає, швидкість "
     "місії задає WP_SPD у м/с, тому встановлено WP_SPD = V."),
]
for i, (head, text) in enumerate(notes):
    wn.write(2 + i * 3, 0, head, fm["note_b"])
    wn.write(3 + i * 3, 0, text, fm["note"])
    wn.set_row(3 + i * 3, 15 * (len(text) // 125 + 1) + 3)

wb.close()
print("Збережено:", OUT)
print("Рядки CSV польоту: %d-%d, рядків: %d, на аркуші %d-%d" % (i0 + 2, i_last + 2, N, FIRST, LAST))
