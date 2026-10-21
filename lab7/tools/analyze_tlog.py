import collections
import datetime
import json
import sys

from pymavlink import mavutil

MAV_MODE_FLAG_SAFETY_ARMED = 128
COPTER_MODES = {0: "Stabilize", 3: "Auto", 4: "Guided", 5: "Loiter", 6: "RTL", 9: "Land"}
VEHICLE_SYSID = 1

def utc(ts):
    return datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

def main():
    path, out_path = sys.argv[1], sys.argv[2]
    link = mavutil.mavlink_connection(path, dialect="ardupilotmega")

    counts = collections.Counter()
    transitions = []
    texts = []
    attitude, vfr, pos = [], [], []
    first_ts = last_ts = None
    prev_state = None

    while True:
        msg = link.recv_match(blocking=False)
        if msg is None:
            break
        ts = getattr(msg, "_timestamp", None)
        kind = msg.get_type()
        if msg.get_srcSystem() != VEHICLE_SYSID and kind != "BAD_DATA":
            continue
        counts[kind] += 1
        if ts:
            first_ts = first_ts or ts
            last_ts = ts
        if kind == "HEARTBEAT" and msg.type == 2:
            state = (COPTER_MODES.get(msg.custom_mode, str(msg.custom_mode)),
                     bool(msg.base_mode & MAV_MODE_FLAG_SAFETY_ARMED))
            if state != prev_state:
                transitions.append({"t": ts, "utc": utc(ts), "mode": state[0], "armed": state[1]})
                prev_state = state
        elif kind == "STATUSTEXT":
            texts.append({"t": ts, "utc": utc(ts), "text": msg.text})
        elif kind == "ATTITUDE":
            attitude.append((ts, msg.roll * 57.29578, msg.pitch * 57.29578))
        elif kind == "VFR_HUD":
            vfr.append((ts, msg.groundspeed, msg.airspeed, msg.alt))
        elif kind == "GLOBAL_POSITION_INT":
            pos.append((ts, msg.lat / 1e7, msg.lon / 1e7, msg.relative_alt / 1000.0, msg.vx / 100.0, msg.vy / 100.0))

    arm_times = [i for i, tr in enumerate(transitions) if tr["armed"] and (i == 0 or not transitions[i - 1]["armed"])]
    t_arm = transitions[arm_times[-1]]["t"] if arm_times else first_ts
    t_disarm = next((tr["t"] for tr in transitions if not tr["armed"] and tr["t"] > t_arm), last_ts)

    def in_flight(rows):
        return [r for r in rows if t_arm <= r[0] <= t_disarm]

    att, hud, gp = in_flight(attitude), in_flight(vfr), in_flight(pos)
    summary = {
        "file": path,
        "first_utc": utc(first_ts), "last_utc": utc(last_ts),
        "message_counts": dict(counts.most_common()),
        "transitions": transitions,
        "arm_utc": utc(t_arm), "disarm_utc": utc(t_disarm),
        "flight_duration_s": round(t_disarm - t_arm, 1),
        "max_abs_roll_deg": round(max(abs(r[1]) for r in att), 2) if att else None,
        "max_abs_pitch_deg": round(max(abs(r[2]) for r in att), 2) if att else None,
        "max_groundspeed_ms": round(max(r[1] for r in hud), 2) if hud else None,
        "max_airspeed_ms": round(max(r[2] for r in hud), 2) if hud else None,
        "max_rel_alt_m": round(max(r[3] for r in gp), 2) if gp else None,
        "start_position": {"lat": gp[0][1], "lon": gp[0][2]} if gp else None,
        "final_position": {"lat": gp[-1][1], "lon": gp[-1][2]} if gp else None,
        "status_texts": [t for t in texts if t["t"] >= t_arm - 5],
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(json.dumps({k: v for k, v in summary.items() if k not in ("message_counts", "status_texts")},
                     ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
