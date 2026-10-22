# Лабораторна робота №7: MAVLink і телеметрія

ArduPilot SITL, Gazebo і QGroundControl: автоматична місія Takeoff, Waypoint, Land і аналіз телеметрії. Варіант 5: висота 50 м, швидкість 5 м/с, ціль −35.3631166; 149.1639735.

## Запуск

Ubuntu 22.04 aarch64 (віртуальна машина), Gazebo Sim 8.15, ArduPilot SITL (ArduCopter), MAVProxy, QGroundControl 5.1.5.

```bash
~/lab7/scripts/setup_qgc.sh
~/lab7/scripts/start_sim.sh
~/lab7/scripts/start_qgc.sh
python3 ~/lab7/tools/make_plan.py ~/lab7/variant.env ~/lab7/variant5.plan
~/lab7/scripts/stop_qgc.sh
~/lab7/scripts/stop_sim.sh
```

`setup_qgc.sh` виконується один раз після завантаження AppImage QGroundControl у `~/lab7/qgc/`. Швидкість місії задається параметром `WP_SPD = 5` (у цій збірці ArduCopter він замінює `WPNAV_SPEED`).

## Вміст

| Файл | Призначення |
|---|---|
| `pazns_lab7_vishnevskiy_ir33.pdf` | звіт |
| `lab7_analysis_vishnevskiy_ir33.xlsx` | показники таблиці 7.4 за CSV з джерелом кожного значення |
| `results/variant5.plan` | план місії для QGroundControl |
| `results/telemetry/` | журнали польоту: `.tlog` і `.csv` |
| `scripts/`, `config/`, `variant.env` | запуск і зупинка середовища |
| `tools/` | план місії (`make_plan.py`), аналіз CSV і `.tlog` |

## Результат

Найбільша висота 50.0 м, швидкість 5.0 м/с, час польоту 114 с, кінцева координата збігається з ціллю.

```bash
python3 tools/analyze_csv.py variant.env "results/telemetry/2026-10-21 21-41-37 vehicle1.csv" results/analysis
```
