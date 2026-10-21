import csv
import datetime
import json
import math
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

def read_env(path):
    values = {}
    for line in open(path, encoding="utf-8"):
        line = line.split("#", 1)[0].strip()
        if "=" in line and "$" not in line:
            key, val = line.split("=", 1)
            values[key] = val
    return values

def hms_to_s(text):
    h, m, s = (int(x) for x in text.split(":"))
    return h * 3600 + m * 60 + s

def haversine_m(lat1, lon1, lat2, lon2):
    r = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))

def main():
    env = read_env(sys.argv[1])
    h_target = float(env["ALT_M"])
    v_target = float(env["SPEED_MS"])
    lat_t, lon_t = float(env["TARGET_LAT"]), float(env["TARGET_LON"])
    out_dir = sys.argv[3]
    os.makedirs(out_dir, exist_ok=True)

    rows = []
    for r in csv.DictReader(open(sys.argv[2], encoding="utf-8")):
        rows.append({
            "ts": datetime.datetime.strptime(r["Timestamp"], "%Y-%m-%d %H:%M:%S.%f"),
            "flight_s": hms_to_s(r["flightTime"]),
            "alt": float(r["altitudeRelative"]),
            "gs": float(r["groundSpeed"]),
            "as": float(r["airSpeed"]),
            "climb": float(r["climbRate"]),
            "roll": float(r["roll"]),
            "lat": float(r["gps.lat"]),
            "lon": float(r["gps.lon"]),
            "dist_home": float(r["distanceToHome"]),
            "flight_dist": float(r["flightDistance"]),
        })

    i0 = 0
    for i in range(1, len(rows)):
        if rows[i]["flight_s"] < rows[i - 1]["flight_s"]:
            i0 = i
    i_peak = max(range(i0, len(rows)), key=lambda i: rows[i]["alt"])
    i_end = next(i for i in range(i_peak, len(rows)) if rows[i]["alt"] < 0.1)
    flight = rows[i0:i_end + 1]
    t0 = flight[0]["ts"]
    for r in flight:
        r["t"] = (r["ts"] - t0).total_seconds()

    i_alt = next(i for i, r in enumerate(flight) if r["alt"] >= 0.99 * h_target)
    cruise = [i for i, r in enumerate(flight) if r["gs"] >= 0.5 and r["alt"] >= 0.95 * h_target]
    i_cruise0, i_cruise1 = cruise[0], cruise[-1]
    t_takeoff_end = flight[i_alt]["t"]
    t_cruise0, t_cruise1 = flight[i_cruise0]["t"], flight[i_cruise1]["t"] + 1.0
    t_end = flight[-1]["t"]

    final = rows[i_end]
    steady = [r["gs"] for r in flight if r["gs"] >= 0.9 * v_target]
    metrics = {
        "variant": int(env["VARIANT"]),
        "csv_rows_total": len(rows),
        "flight_rows": len(flight),
        "flight_start_utc": t0.strftime("%Y-%m-%d %H:%M:%S"),
        "touchdown_utc": final["ts"].strftime("%Y-%m-%d %H:%M:%S"),
        "takeoff_phase_s": round(t_takeoff_end, 1),
        "cruise_phase_s": [round(t_cruise0, 1), round(t_cruise1, 1)],
        "landing_phase_s": [round(t_cruise1, 1), round(t_end, 1)],
        "max_alt_m": max(r["alt"] for r in flight),
        "max_groundspeed_ms": max(r["gs"] for r in flight),
        "max_airspeed_ms": max(r["as"] for r in flight),
        "steady_groundspeed_ms": round(sum(steady) / len(steady), 2),
        "max_climb_ms": max(r["climb"] for r in flight),
        "max_descent_ms": min(r["climb"] for r in flight),
        "flight_time_qgc_s": final["flight_s"],
        "flight_time_by_rows_s": round(t_end, 1),
        "max_abs_roll_csv_deg": max(abs(r["roll"]) for r in flight),
        "start": {"lat": flight[0]["lat"], "lon": flight[0]["lon"]},
        "end": {"lat": final["lat"], "lon": final["lon"]},
        "target_error_m": round(haversine_m(final["lat"], final["lon"], lat_t, lon_t), 2),
        "distance_home_target_m": flight[-1]["dist_home"],
        "flight_distance_m": final["flight_dist"],
        "alt_error_m": round(max(r["alt"] for r in flight) - h_target, 2),
    }
    with open(os.path.join(out_dir, "metrics_csv.json"), "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})
    phases = [(0, t_takeoff_end, "#cfe3f7", "Зліт"),
              (t_takeoff_end, t_cruise0, "#ffffff", ""),
              (t_cruise0, t_cruise1, "#d5efd2", "Горизонтальний політ"),
              (t_cruise1, t_end, "#fbe3c5", "Посадка")]

    def plot(key, ylabel, fname, color, hline=None, hlabel=None):
        fig, ax = plt.subplots(figsize=(8.2, 3.6), dpi=200)
        for a, b, c, label in phases:
            ax.axvspan(a, b, color=c, lw=0)
            if label:
                ax.text((a + b) / 2, 1.02, label, transform=ax.get_xaxis_transform(), ha="center",
                        va="bottom", fontsize=9)
        ax.plot([r["t"] for r in flight], [r[key] for r in flight], color=color, lw=1.8, marker="o", ms=2.8)
        if hline is not None:
            ax.axhline(hline, color="#555555", lw=1, ls="--", label=hlabel)
            ax.legend(loc="center right", frameon=False)
        ax.set_xlabel("Час від початку польоту, с")
        ax.set_ylabel(ylabel)
        ax.set_xlim(0, t_end)
        lo = min(r[key] for r in flight)
        ax.set_ylim(min(0, lo * 1.1) if lo < 0 else 0, max(r[key] for r in flight) * 1.15 or 1)
        ax.grid(alpha=0.35)
        fig.tight_layout()
        fig.savefig(os.path.join(out_dir, fname))
        plt.close(fig)

    plot("alt", "Висота відносно точки старту, м", "plot_altitude.png", "#1f5fa8", h_target, f"задана висота H = {h_target:g} м")
    plot("as", "Повітряна швидкість, м/с", "plot_airspeed.png", "#b3472d", v_target, f"задана швидкість V = {v_target:g} м/с")
    plot("gs", "Наземна швидкість, м/с", "plot_groundspeed.png", "#2e7d32", v_target, f"задана швидкість V = {v_target:g} м/с")

    lat0, lon0 = flight[0]["lat"], flight[0]["lon"]
    k_lat, k_lon = 111320.0, 111320.0 * math.cos(math.radians(lat0))
    xs = [(r["lon"] - lon0) * k_lon for r in flight]
    ys = [(r["lat"] - lat0) * k_lat for r in flight]
    tx, ty = (lon_t - lon0) * k_lon, (lat_t - lat0) * k_lat
    fig, ax = plt.subplots(figsize=(8.2, 3.2), dpi=200)
    ax.plot(xs, ys, color="#1f5fa8", lw=1.8, marker="o", ms=2.8, label="траєкторія за CSV (1 Гц)")
    ax.plot([0], [0], marker="s", color="#2e7d32", ms=7, ls="", label="точка старту")
    ax.plot([tx], [ty], marker="*", color="#b3472d", ms=13, ls="", label="цільова точка")
    ax.set_aspect("equal", adjustable="datalim")
    ax.set_xlabel("Схід від точки старту, м")
    ax.set_ylabel("Північ від точки старту, м")
    ax.grid(alpha=0.35)
    ax.legend(loc="upper center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.18))
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "plot_trajectory.png"))
    plt.close(fig)

    print(json.dumps(metrics, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
