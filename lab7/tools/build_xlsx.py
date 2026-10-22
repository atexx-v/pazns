import csv
import datetime
import math
import os

import xlsxwriter
from xlsxwriter.utility import xl_col_to_name

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(ROOT, "results", "telemetry", "2026-10-21 21-41-37 vehicle1.csv")
OUT = os.path.join(ROOT, "lab7_analysis_vishnevskiy_ir33.xlsx")
EPOCH = datetime.datetime(1899, 12, 30)


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
need = ["Timestamp", "flightTime", "altitudeRelative", "groundSpeed", "airSpeed", "roll", "gps.lat", "gps.lon",
        "climbRate", "distanceToHome", "flightDistance"]
letter = {n: xl_col_to_name(col[n]) for n in need}

stamps = [datetime.datetime.strptime(r[col["Timestamp"]], "%Y-%m-%d %H:%M:%S.%f") for r in body]
fsec = [hms(r[col["flightTime"]]) for r in body]
alt = [float(r[col["altitudeRelative"]]) for r in body]

i0 = 0
for i in range(1, len(body)):
    if fsec[i] < fsec[i - 1]:
        i0 = i
peak = max(range(i0, len(body)), key=lambda i: alt[i])
final_f = max(fsec[i0:])
i_last = next(i for i in range(peak, len(body)) if fsec[i] == final_f)
N = i_last - i0 + 1
LAST = N + 1

wb = xlsxwriter.Workbook(OUT)
base = {"font_name": "Arial", "font_size": 11}
fmt = {
    "plain": wb.add_format(base),
    "title": wb.add_format(dict(base, bold=True, font_size=14)),
    "bold": wb.add_format(dict(base, bold=True)),
    "head": wb.add_format(dict(base, bold=True, bg_color="#D9D9D9", border=1, text_wrap=True, valign="vcenter")),
    "cell": wb.add_format(dict(base, border=1, text_wrap=True, valign="vcenter")),
    "n0": wb.add_format(dict(base, border=1, num_format="0", valign="vcenter")),
    "n1": wb.add_format(dict(base, border=1, num_format="0.0", valign="vcenter")),
    "n2": wb.add_format(dict(base, border=1, num_format="0.00", valign="vcenter")),
    "n7": wb.add_format(dict(base, num_format="0.0000000")),
    "dt": wb.add_format(dict(base, num_format="yyyy-mm-dd hh:mm:ss.000")),
    "tm": wb.add_format(dict(base, num_format="[h]:mm:ss")),
    "dec1": wb.add_format(dict(base, num_format="0.0")),
    "dec2": wb.add_format(dict(base, num_format="0.00")),
    "note": wb.add_format(dict(base, text_wrap=True, valign="top")),
}

ws_a = wb.add_worksheet("Аналіз")
ws_f = wb.add_worksheet("Політ")
ws_c = wb.add_worksheet("CSV")

for j, name in enumerate(header):
    ws_c.write(0, j, name, fmt["bold"])
for i, row in enumerate(body):
    for j, value in enumerate(row):
        if j == col["Timestamp"]:
            ws_c.write_datetime(i + 1, j, stamps[i], fmt["dt"])
        else:
            cell = to_cell(value)
            if isinstance(cell, float):
                ws_c.write_number(i + 1, j, cell)
            else:
                ws_c.write_string(i + 1, j, cell)
ws_c.freeze_panes(1, 1)
ws_c.set_column(col["Timestamp"], col["Timestamp"], 24)

fheads = ["Timestamp", "flightTime", "altitudeRelative, м", "groundSpeed, м/с", "airSpeed, м/с", "roll, град",
          "gps.lat", "gps.lon", "climbRate, м/с", "distanceToHome, м", "flightDistance, м", "t, с",
          "висота ≥ 0,99·H", "t горизонтального польоту, с", "Етап"]
for j, h in enumerate(fheads):
    ws_f.write(0, j, h, fmt["head"])
ws_f.set_row(0, 45)
ws_f.set_column(0, 0, 24)
ws_f.set_column(1, 14, 15)
ws_f.freeze_panes(1, 0)

t0 = stamps[i0]
tvals = [(stamps[i0 + k] - t0).total_seconds() for k in range(N)]
t_take = next(tvals[k] for k in range(N) if alt[i0 + k] >= 0.99 * H)
cruise_t = [tvals[k] for k in range(N)
            if float(body[i0 + k][col["groundSpeed"]]) >= 0.5 and alt[i0 + k] >= 0.95 * H]
t_c0, t_c1, t_end = min(cruise_t), max(cruise_t) + 1, max(tvals)

dest_col = {2: "altitudeRelative", 3: "groundSpeed", 4: "airSpeed", 5: "roll", 6: "gps.lat", 7: "gps.lon",
            8: "climbRate", 9: "distanceToHome", 10: "flightDistance"}
for k in range(N):
    r = i0 + k + 2
    n = k + 2
    row = body[i0 + k]
    ws_f.write_formula(n - 1, 0, "='CSV'!%s%d" % (letter["Timestamp"], r), fmt["dt"], serial(stamps[i0 + k]))
    ws_f.write_formula(n - 1, 1, "=TIMEVALUE('CSV'!%s%d)" % (letter["flightTime"], r), fmt["tm"], fsec[i0 + k] / 86400)
    for c, name in dest_col.items():
        f_ = fmt["n7"] if name in ("gps.lat", "gps.lon") else fmt["plain"]
        ws_f.write_formula(n - 1, c, "='CSV'!%s%d" % (letter[name], r), f_, float(row[col[name]]))
    ws_f.write_formula(n - 1, 11, "=(A%d-$A$2)*86400" % n, fmt["dec1"], tvals[k])
    flag = 1 if alt[i0 + k] >= 0.99 * H else 0
    ws_f.write_formula(n - 1, 12, "=IF(C%d>=0.99*'Аналіз'!$B$3,1,0)" % n, fmt["plain"], flag)
    in_cruise = float(row[col["groundSpeed"]]) >= 0.5 and alt[i0 + k] >= 0.95 * H
    ws_f.write_formula(n - 1, 13, "=IF(AND(D%d>=0.5,C%d>=0.95*'Аналіз'!$B$3),L%d,\"\")" % (n, n, n), fmt["dec1"],
                       tvals[k] if in_cruise else "")
    tk = tvals[k]
    stage = "Зліт" if tk <= t_take else ("Перехід" if tk < t_c0 else ("Горизонтальний політ" if tk < t_c1 else "Посадка"))
    ws_f.write_formula(n - 1, 14,
                       "=IF(L%d<='Аналіз'!$B$11,\"Зліт\",IF(L%d<'Аналіз'!$B$12,\"Перехід\",IF(L%d<'Аналіз'!$B$13,\"Горизонтальний політ\",\"Посадка\")))" % (n, n, n),
                       fmt["plain"], stage)

R = "'Політ'!"
rng = lambda c: "%s$%s$2:$%s$%d" % (R, c, c, LAST)

ws_a.set_column(0, 0, 44)
ws_a.set_column(1, 1, 34)
ws_a.set_column(2, 2, 14)
ws_a.set_column(3, 3, 52)
ws_a.write(0, 0, "Лабораторна робота №7, варіант 5. Аналіз телеметрії QGroundControl (CSV)", fmt["title"])
ws_a.write(1, 0, "Дані: аркуш «CSV» (повний файл QGC). Політ виділено на аркуші «Політ» (рядки CSV %d–%d), усі значення нижче обчислено формулами."
           % (i0 + 2, i_last + 2), fmt["plain"])

params = [
    (3, "Висота зльоту H", H, "м", "Таблиця 7.6, варіант 5"),
    (4, "Горизонтальна швидкість V", V, "м/с", "Таблиця 7.6, варіант 5"),
    (5, "Цільова точка, широта", LAT_T, "°", "Таблиця 7.6, варіант 5"),
    (6, "Цільова точка, довгота", LON_T, "°", "Таблиця 7.6, варіант 5"),
]
for r, label, val, unit, source in params:
    ws_a.write(r - 1, 0, label, fmt["cell"])
    ws_a.write_number(r - 1, 1, val, fmt["n7"] if r in (5, 6) else fmt["n1"])
    ws_a.write(r - 1, 2, unit, fmt["cell"])
    ws_a.write(r - 1, 3, source, fmt["cell"])
ws_a.write(6, 0, "WPNAV_SPEED = 100 · V", fmt["cell"])
ws_a.write_formula(6, 1, "=100*B4", fmt["n0"], 100 * V)
ws_a.write(6, 2, "см/с", fmt["cell"])
ws_a.write(6, 3, "Формула методички (у ArduCopter 4.8 параметра немає)", fmt["cell"])
ws_a.write(7, 0, "WP_SPD (замінник WPNAV_SPEED)", fmt["cell"])
ws_a.write_formula(7, 1, "=B4", fmt["n1"], V)
ws_a.write(7, 2, "м/с", fmt["cell"])
ws_a.write(7, 3, "Параметр, який задано в QGroundControl", fmt["cell"])

ws_a.write(9, 0, "Межі етапів польоту (за даними)", fmt["bold"])
bounds = [
    (11, "Кінець зльоту (висота ≥ 0,99·H)", "=INDEX(%s,MATCH(1,%s,0))" % (rng("L"), rng("M")), t_take),
    (12, "Початок горизонтального польоту", "=MIN(%s)" % rng("N"), t_c0),
    (13, "Кінець горизонтального польоту", "=MAX(%s)+1" % rng("N"), t_c1),
    (14, "Кінець польоту (disarm)", "=MAX(%s)" % rng("L"), t_end),
]
for r, label, formula, val in bounds:
    ws_a.write(r - 1, 0, label, fmt["cell"])
    ws_a.write_formula(r - 1, 1, formula, fmt["n1"], val)
    ws_a.write(r - 1, 2, "с", fmt["cell"])
    ws_a.write(r - 1, 3, "Timestamp, altitudeRelative, groundSpeed", fmt["cell"])

ws_a.write(15, 0, "Таблиця 7.4 – Результати аналізу телеметрії", fmt["bold"])
for j, h in enumerate(["Показник", "Значення", "Одиниця", "Джерело значення (стовпець CSV / повідомлення MAVLink)"]):
    ws_a.write(16, j, h, fmt["head"])

alts = [float(body[i0 + k][col["altitudeRelative"]]) for k in range(N)]
gs = [float(body[i0 + k][col["groundSpeed"]]) for k in range(N)]
asp = [float(body[i0 + k][col["airSpeed"]]) for k in range(N)]
roll = [float(body[i0 + k][col["roll"]]) for k in range(N)]
lat = [float(body[i0 + k][col["gps.lat"]]) for k in range(N)]
lon = [float(body[i0 + k][col["gps.lon"]]) for k in range(N)]
dh = float(body[i_last][col["distanceToHome"]])
fd = float(body[i_last][col["flightDistance"]])
err = haversine(lat[-1], lon[-1], LAT_T, LON_T)

rows74 = [
    ("Час зльоту (arm, початок набору висоти)", '=TEXT(%sA2,"hh:mm:ss")' % R, stamps[i0].strftime("%H:%M:%S"), "UTC",
     "Timestamp, перший рядок польоту", fmt["cell"]),
    ("Тривалість набору висоти H", "=B11", t_take, "с", "Timestamp, altitudeRelative ≥ 0,99·H", fmt["n0"]),
    ("Найбільша висота", "=MAX(%s)" % rng("C"), max(alts), "м", "altitudeRelative", fmt["n1"]),
    ("Найбільша швидкість (наземна)", "=MAX(%s)" % rng("D"), max(gs), "м/с", "groundSpeed", fmt["n1"]),
    ("Найбільша швидкість (повітряна)", "=MAX(%s)" % rng("E"), max(asp), "м/с", "airSpeed (оцінка автопілота)", fmt["n1"]),
    ("Час польоту", "=%sB%d*86400" % (R, LAST), final_f, "с", "flightTime (лічильник QGC, останнє значення)", fmt["n0"]),
    ("Початкова координата", '=TEXT(%sG2,"0.0000000")&"; "&TEXT(%sH2,"0.0000000")' % (R, R),
     "%.7f; %.7f" % (lat[0], lon[0]), "°", "gps.lat, gps.lon (перший рядок польоту)", fmt["cell"]),
    ("Кінцева координата", '=TEXT(%sG%d,"0.0000000")&"; "&TEXT(%sH%d,"0.0000000")' % (R, LAST, R, LAST),
     "%.7f; %.7f" % (lat[-1], lon[-1]), "°", "gps.lat, gps.lon (останній рядок польоту)", fmt["cell"]),
    ("Максимальний roll", "=MAX(MAX(%s),-MIN(%s))" % (rng("F"), rng("F")), max(max(roll), -min(roll)), "град", "roll", fmt["n1"]),
]
for i, (label, formula, val, unit, source, f_) in enumerate(rows74):
    r = 17 + i
    ws_a.write(r, 0, label, fmt["cell"])
    ws_a.write_formula(r, 1, formula, f_, val)
    ws_a.write(r, 2, unit, fmt["cell"])
    ws_a.write(r, 3, source, fmt["cell"])
r = 17 + len(rows74)
ws_a.write(r, 0, "Режими польоту", fmt["cell"])
ws_a.write(r, 1, "Stabilize → Guided → Auto", fmt["cell"])
ws_a.write(r, 2, "", fmt["cell"])
ws_a.write(r, 3, ".tlog: HEARTBEAT, custom_mode (0 → 4 → 3); у CSV QGC такого стовпця немає", fmt["cell"])
ws_a.write(r + 1, 0, "Стан arm до та після місії", fmt["cell"])
ws_a.write(r + 1, 1, "до: disarmed; у польоті: armed; після: disarmed", fmt["cell"])
ws_a.write(r + 1, 2, "", fmt["cell"])
ws_a.write(r + 1, 3, ".tlog: HEARTBEAT, base_mode, біт 128 (armed)", fmt["cell"])
ws_a.set_row(r + 1, 32)

cmp_row = r + 3
ws_a.write(cmp_row, 0, "Порівняння заданого з фактичним", fmt["bold"])
for j, h in enumerate(["Параметр", "Задано", "Фактично", "Відхилення"]):
    ws_a.write(cmp_row + 1, j, h, fmt["head"])
hv = ("2*6371000*ASIN(SQRT(SIN(RADIANS(%sG%d-B5)/2)^2+COS(RADIANS(B5))*COS(RADIANS(%sG%d))*SIN(RADIANS(%sH%d-B6)/2)^2))"
      % (R, LAST, R, LAST, R, LAST))
cmp_rows = [
    ("Висота, м", "=B3", H, "=B20", max(alts), "=C%d-B%d", fmt["n2"]),
    ("Швидкість, м/с", "=B4", V, "=B21", max(gs), "=C%d-B%d", fmt["n2"]),
    ("Відстань від цільової точки, м", "=0", 0.0, "=" + hv, err, "=C%d-B%d", fmt["n2"]),
]
for i, (label, f_set, v_set, f_fact, v_fact, f_dev, nf) in enumerate(cmp_rows):
    rr = cmp_row + 2 + i
    ws_a.write(rr, 0, label, fmt["cell"])
    ws_a.write_formula(rr, 1, f_set, nf, v_set)
    ws_a.write_formula(rr, 2, f_fact, nf, v_fact)
    ws_a.write_formula(rr, 3, f_dev % (rr + 1, rr + 1), nf, v_fact - v_set)
rr = cmp_row + 5
ws_a.write(rr, 0, "Відстань старт → ціль (distanceToHome), м", fmt["cell"])
ws_a.write_formula(rr, 1, "=%sJ%d" % (R, LAST), fmt["n1"], dh)
ws_a.write(rr, 2, "", fmt["cell"])
ws_a.write(rr, 3, "distanceToHome, останній рядок", fmt["cell"])
ws_a.write(rr + 1, 0, "Пройдена відстань (flightDistance), м", fmt["cell"])
ws_a.write_formula(rr + 1, 1, "=%sK%d" % (R, LAST), fmt["n1"], fd)
ws_a.write(rr + 1, 2, "", fmt["cell"])
ws_a.write(rr + 1, 3, "flightDistance, останній рядок", fmt["cell"])

notes_row = rr + 3
ws_a.write(notes_row, 0, "Примітки", fmt["bold"])
notes = [
    "Вісь часу t = Timestamp − Timestamp першого рядка польоту. У CSV є й інші стовпці часу: flightTime (лічильник польоту QGC у форматі "
    "год:хв:с, крок 1 с, скидається при кожному arm і зупиняється після disarm), clock.currentTime і clock.currentUTCTime (годинник апарата), "
    "hobbs, timeToHome (оцінка часу повернення). Для осі часу обрано Timestamp (безперервний ряд із дробовою секундою), «Час польоту» взято з flightTime.",
    "Політ виділено так: початок – останнє скидання flightTime (початок останнього arm), кінець – рядок, де flightTime зупиняється після disarm. "
    "CSV QGC пишеться безперервно, тому містить і рядки до та після польоту.",
    "airSpeed у ArduCopter без датчика швидкості повітря є оцінкою автопілота; у симуляції немає вітру, тому вона майже збігається з groundSpeed.",
    "У CSV QGC немає режиму польоту і стану arm, їх взято з .tlog (повідомлення HEARTBEAT).",
]
for i, text in enumerate(notes):
    ws_a.merge_range(notes_row + 1 + i, 0, notes_row + 1 + i, 3, text, fmt["note"])
    ws_a.set_row(notes_row + 1 + i, 62 if i == 0 else 34)

hrow = notes_row + len(notes) + 3
ws_a.write(hrow, 0, "Допоміжні дані для діаграм", fmt["bold"])
helpers = [
    ("Задана висота H", "0", 0, "=B3", H, "=B14", t_end, "=B3", H),
    ("Задана швидкість V", "0", 0, "=B4", V, "=B14", t_end, "=B4", V),
    ("Кінець зльоту (висота)", "=B11", t_take, "0", 0, "=B11", t_take, "=B3*1.1", H * 1.1),
    ("Кінець горизонтального польоту (висота)", "=B13", t_c1, "0", 0, "=B13", t_c1, "=B3*1.1", H * 1.1),
    ("Кінець зльоту (швидкість)", "=B11", t_take, "0", 0, "=B11", t_take, "=B4*1.2", V * 1.2),
    ("Кінець горизонтального польоту (швидкість)", "=B13", t_c1, "0", 0, "=B13", t_c1, "=B4*1.2", V * 1.2),
]
helper_pos = {}
for i, (label, x1f, x1v, y1f, y1v, x2f, x2v, y2f, y2v) in enumerate(helpers):
    base_row = hrow + 1 + i * 3
    ws_a.write(base_row, 0, label, fmt["plain"])
    for k, (xf, xv, yf, yv) in enumerate([(x1f, x1v, y1f, y1v), (x2f, x2v, y2f, y2v)]):
        x_formula = xf if xf.startswith("=") else "=" + xf
        y_formula = yf if yf.startswith("=") else "=" + yf
        ws_a.write_formula(base_row + 1 + k, 0, x_formula, fmt["dec1"], xv)
        ws_a.write_formula(base_row + 1 + k, 1, y_formula, fmt["dec1"], yv)
    helper_pos[i] = base_row + 2


def aref(i):
    first = helper_pos[i]
    return "='Аналіз'!$A$%d:$A$%d" % (first, first + 1), "='Аналіз'!$B$%d:$B$%d" % (first, first + 1)


def chart(title, ycol, ylabel, set_idx, bound_idx, color, line_label, cell):
    ch = wb.add_chart({"type": "scatter", "subtype": "straight_with_markers"})
    ch.add_series({
        "name": title,
        "categories": "='Політ'!$L$2:$L$%d" % LAST,
        "values": "='Політ'!$%s$2:$%s$%d" % (ycol, ycol, LAST),
        "line": {"color": color, "width": 2.0},
        "marker": {"type": "circle", "size": 4, "fill": {"color": color}, "border": {"color": color}},
    })
    x, y = aref(set_idx)
    ch.add_series({"name": line_label, "categories": x, "values": y,
                   "line": {"color": "#555555", "width": 1.25, "dash_type": "dash"}, "marker": {"type": "none"}})
    for idx, label in zip(bound_idx, ["Кінець зльоту", "Кінець горизонтального польоту"]):
        x, y = aref(idx)
        ch.add_series({"name": label, "categories": x, "values": y,
                       "line": {"color": "#9e9e9e", "width": 1.0, "dash_type": "round_dot"}, "marker": {"type": "none"}})
    ch.set_title({"name": title + " від часу", "name_font": {"name": "Arial", "size": 12}})
    ch.set_x_axis({"name": "Час від початку польоту, с", "min": 0, "max": math.ceil(t_end),
                   "major_gridlines": {"visible": True, "line": {"color": "#dddddd"}}})
    ch.set_y_axis({"name": ylabel, "min": 0, "major_gridlines": {"visible": True, "line": {"color": "#dddddd"}}})
    ch.set_legend({"position": "bottom"})
    ch.set_size({"width": 760, "height": 340})
    ws_a.insert_chart(cell, ch)


chart("Висота", "C", "Висота відносно точки старту, м", 0, (2, 3), "#1f5fa8", "Задана висота H", "F3")
chart("Повітряна швидкість", "E", "Повітряна швидкість, м/с", 1, (4, 5), "#b3472d", "Задана швидкість V", "F21")
chart("Наземна швидкість", "D", "Наземна швидкість, м/с", 1, (4, 5), "#2e7d32", "Задана швидкість V", "F39")

ws_a.set_landscape()
ws_a.set_paper(9)
ws_a.fit_to_pages(1, 0)
ws_a.activate()
wb.close()
print("Збережено:", OUT)
print("Рядки CSV польоту: %d-%d, рядків: %d" % (i0 + 2, i_last + 2, N))
