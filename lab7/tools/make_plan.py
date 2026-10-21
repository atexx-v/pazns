import json
import sys

HOME = [-35.3632621, 149.1652374, 10]

CMD_WAYPOINT, CMD_LAND, CMD_TAKEOFF = 16, 21, 22
FRAME_REL_ALT = 3

def read_env(path):
    values = {}
    for line in open(path, encoding="utf-8"):
        line = line.split("#", 1)[0].strip()
        if "=" in line and "$" not in line:
            key, val = line.split("=", 1)
            values[key] = val
    return values

def item(seq, command, lat, lon, alt):
    return {
        "AMSLAltAboveTerrain": None,
        "Altitude": alt,
        "AltitudeMode": 1,
        "autoContinue": True,
        "command": command,
        "doJumpId": seq,
        "frame": FRAME_REL_ALT,
        "params": [0, 0, 0, None, lat, lon, alt],
        "type": "SimpleItem",
    }

def main():
    env = read_env(sys.argv[1])
    alt = float(env["ALT_M"])
    speed = float(env["SPEED_MS"])
    lat, lon = float(env["TARGET_LAT"]), float(env["TARGET_LON"])

    plan = {
        "fileType": "Plan",
        "geoFence": {"circles": [], "polygons": [], "version": 2},
        "groundStation": "QGroundControl",
        "mission": {
            "cruiseSpeed": speed,
            "firmwareType": 3,
            "globalPlanAltitudeMode": 1,
            "hoverSpeed": speed,
            "items": [
                item(1, CMD_TAKEOFF, 0, 0, alt),
                item(2, CMD_WAYPOINT, lat, lon, alt),
                item(3, CMD_LAND, lat, lon, 0),
            ],
            "plannedHomePosition": HOME,
            "vehicleType": 2,
            "version": 2,
        },
        "rallyPoints": {"points": [], "version": 2},
        "version": 1,
    }
    with open(sys.argv[2], "w", encoding="utf-8") as out:
        json.dump(plan, out, indent=2)
    print(f"План записано: {sys.argv[2]} (H = {alt:g} м, V = {speed:g} м/с, ціль {lat}; {lon})")

if __name__ == "__main__":
    main()
