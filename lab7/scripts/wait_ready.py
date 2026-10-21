import sys
import time

from pymavlink import mavutil

PREARM_CHECK = 0x10000000

timeout = float(sys.argv[1]) if len(sys.argv) > 1 else 180

link = mavutil.mavlink_connection("udpin:127.0.0.1:14551")
start = time.time()

while time.time() - start < timeout:
    if link.wait_heartbeat(timeout=2):
        break
else:
    print("HEARTBEAT не отримано")
    sys.exit(1)
print(f"HEARTBEAT від системи {link.target_system} через {time.time() - start:.0f} с")

while time.time() - start < timeout:
    msg = link.recv_match(type="SYS_STATUS", blocking=True, timeout=2)
    if msg is None:
        continue
    if msg.onboard_control_sensors_health & PREARM_CHECK:
        print(f"Готово: дрон готовий до arm (через {time.time() - start:.0f} с).")
        sys.exit(0)

sys.exit(1)
