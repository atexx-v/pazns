# Програмно-апаратне забезпечення систем рухомих об'єктів

Вишневський Артем, ІР-33. Лабораторні роботи №2, №7 і №9, варіант 5.

| Папка | Робота | Зміст |
|---|---|---|
| `lab2/` | №2 | Gazebo, ArduPilot SITL і ROS 2: політ дрона до заданої точки з автопосадкою |
| `lab7/` | №7 | MAVLink і телеметрія: ArduPilot SITL, Gazebo і QGroundControl, автоматична місія, аналіз `.tlog` і `.csv` |
| `lab9/` | №9 | Кріплення VTX: модель у Fusion (`f3d`) і файл для друку (`stl`) |

У кожній папці з кодом свій `README.md` або скрипти запуску (`scripts/`).

## Лабораторна 2

Ubuntu 22.04, ROS 2 Humble, Gazebo Harmonic, ArduPilot SITL. Варіант 5: Δx = 7.0, Δy = −0.1. Похибка перед посадкою 0.11 м.

```bash
~/lab2/scripts/start_sim.sh
~/lab2/scripts/run_goto.sh
~/lab2/scripts/stop_sim.sh
```

## Лабораторна 7

Ubuntu 22.04 aarch64, Gazebo Sim 8.15, ArduPilot SITL (ArduCopter), MAVProxy, QGroundControl 5.1.5. Варіант 5: висота 50 м, швидкість 5 м/с, ціль −35.3631166; 149.1639735. Кінцева точка збігається з ціллю.

```bash
~/lab7/scripts/start_sim.sh
~/lab7/scripts/start_qgc.sh
```

Опис, результати та звіт: `lab7/README.md`, `lab7/pazns_lab7_vishnevskiy_ir33.pdf`.
