# Програмно-апаратне забезпечення систем рухомих об'єктів

Вишневський Артем, ІР-33. Лабораторні роботи №2, №7 і №9, варіант 5.

| Папка | Робота | Зміст |
|---|---|---|
| `lab2/` | №2 | Gazebo, ArduPilot SITL і ROS 2: політ дрона до заданої точки з автопосадкою |
| `lab7/` | №7 | MAVLink і телеметрія: ArduPilot SITL, Gazebo і QGroundControl, автоматична місія, аналіз `.tlog` і `.csv` |
| `lab9/` | №9 | Проєктування і 3D-друк кріплення VTX AKK Ultra Long Range 3W для рами GEPRC Mark4 10″ в Autodesk Fusion |

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

## Лабораторна 9

Autodesk Fusion. Варіант 5: рама GEPRC Mark4 10″, відеопередавач AKK Ultra Long Range 3W. Внутрішнє розміщення неможливе через колізії зі стійками й гвинтами та зайняту камерою й FC/ESC-стеком, тому VTX встановлено в задній частині рами рамковим кріпленням із прорізами, які не перекривають вентилятор. У тримачі антени є отвір для фіксації кабелю. Перевірка колізій: «No interferences detected».

- `lab9/f3d/lab9_vishnevskyi.f3d` модель у Fusion (Git LFS)
- `lab9/stl/vtx_case.stl` модель для друку

Матеріал PC/ABS, друк кріпильною планкою вниз, внутрішня кишеня 36×36×18 мм із запасом 0.5 мм з кожного боку, стінки 2 мм, монтажний патерн 30.5×30.5 мм.
