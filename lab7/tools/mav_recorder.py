import csv
import sys
import time

from pymavlink import mavutil

MAV_MODE_FLAG_SAFETY_ARMED = 128
COPTER_MODES = {0: "Stabilize", 3: "Auto", 4: "Guided", 5: "Loiter", 6: "RTL", 9: "Land"}

out_path = sys.argv[1]
grace_s = float(sys.argv[2]) if len(sys.argv) > 2 else 5.0
max_s = float(sys.argv[3]) if len(sys.argv) > 3 else 600.0

link = mavutil.mavlink_connection("udpin:127.0.0.1:14551")
link.wait_heartbeat(timeout=10)

last = {}
armed_seen = False
disarmed_at = None
prev_mode, prev_armed = None, None
t0 = time.time()
next_tick = t0

with open(out_path, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["t_wall", "t_boot_s", "lat", "lon", "rel_alt_m", "vx_ms", "vy_ms", "vz_ms",
                "groundspeed_ms", "airspeed_ms", "roll_deg", "pitch_deg", "yaw_deg",
                "mode", "armed", "battery_pct"])
    while time.time() - t0 < max_s:
        msg = link.recv_match(blocking=True, timeout=0.2)
        if msg is not None:
            kind = msg.get_type()
            if kind in ("GLOBAL_POSITION_INT", "VFR_HUD", "ATTITUDE", "SYS_STATUS"):
                last[kind] = msg
            elif kind == "HEARTBEAT" and msg.get_srcSystem() == link.target_system and msg.type == 2:
                last[kind] = msg
                mode = COPTER_MODES.get(msg.custom_mode, str(msg.custom_mode))
                armed = bool(msg.base_mode & MAV_MODE_FLAG_SAFETY_ARMED)
                if mode != prev_mode or armed != prev_armed:
                    print("%.1f c: режим=%s armed=%s" % (time.time() - t0, mode, armed), flush=True)
                    prev_mode, prev_armed = mode, armed
                if armed:
                    armed_seen, disarmed_at = True, None
                elif armed_seen and disarmed_at is None:
                    disarmed_at = time.time()
            elif kind == "STATUSTEXT":
                print("%.1f c: AP: %s" % (time.time() - t0, msg.text), flush=True)

        now = time.time()
        if now >= next_tick and {"GLOBAL_POSITION_INT", "VFR_HUD", "ATTITUDE", "HEARTBEAT"} <= last.keys():
            next_tick += 0.1
            g, v, a, h = last["GLOBAL_POSITION_INT"], last["VFR_HUD"], last["ATTITUDE"], last["HEARTBEAT"]
            s = last.get("SYS_STATUS")
            w.writerow(["%.3f" % now, "%.3f" % (g.time_boot_ms / 1000.0), "%.7f" % (g.lat / 1e7), "%.7f" % (g.lon / 1e7),
                        "%.2f" % (g.relative_alt / 1000.0), "%.2f" % (g.vx / 100.0), "%.2f" % (g.vy / 100.0),
                        "%.2f" % (g.vz / 100.0), "%.2f" % v.groundspeed, "%.2f" % v.airspeed,
                        "%.2f" % (a.roll * 57.29578), "%.2f" % (a.pitch * 57.29578), "%.2f" % (a.yaw * 57.29578),
                        COPTER_MODES.get(h.custom_mode, h.custom_mode), int(bool(h.base_mode & MAV_MODE_FLAG_SAFETY_ARMED)),
                        s.battery_remaining if s else ""])
        if disarmed_at is not None and now - disarmed_at > grace_s:
            break
print("Запис завершено: %s" % out_path)
