# Лабораторна робота №7: MAVLink і телеметрія (ArduPilot SITL + Gazebo + QGroundControl)

Автоматична місія Takeoff -> Waypoint -> Land у симуляції, збереження і аналіз телеметрії QGroundControl.
Варіант 5: H = 50 м, V = 5 м/с, ціль -35.3631166; 149.1639735 (таблиця 7.6 методички).

## Середовище

| Компонент | Версія |
|---|---|
| Хост | MacBook Air, Apple M2 (arm64), macOS 27.0.1, UTM 4.7.5 |
| ОС у VM | Ubuntu 22.04.5 LTS, aarch64, ядро 5.15.0-198 (4 ядра, 6 ГБ RAM) |
| Gazebo | Gazebo Sim 8.15.0 (Harmonic), світ `iris_runway.sdf` з `ardupilot_gazebo` |
| ArduPilot SITL | ArduCopter V4.8.0-dev, коміт `665c0dee` |
| ardupilot_gazebo | коміт `cc0290d` |
| MAVProxy | 1.8.74 |
| QGroundControl | v5.1.5, `QGroundControl-aarch64.AppImage` |
| Python | 3.10.12, pymavlink 2.4.49 (VM); 3.9 + matplotlib 3.9.4 (аналіз на Mac) |

Усі компоненти працюють у віртуальній машині: Gazebo-сервер, SITL, MAVProxy і QGroundControl на віртуальному
дисплеї Xvfb. Вікно QGC доступне з Mac по VNC (`vnc://<IP VM>:5901`), вікно Gazebo - `vnc://<IP VM>:5902`.

## Розгортання

Gazebo, SITL і робочий простір `ros2_ws` розгорнуто за інструкцією лабораторної №2 (`../lab2/README.md`). ROS 2 у цій
роботі не використовується, з `ros2_ws` беруться бінарник `arducopter`, плагін `ardupilot_gazebo` і світи.

```bash
mkdir -p ~/lab7/qgc && cd ~/lab7/qgc
curl -L -C - --retry 20 -o QGroundControl-aarch64.AppImage \
    https://github.com/mavlink/qgroundcontrol/releases/download/v5.1.5/QGroundControl-aarch64.AppImage
~/lab7/scripts/setup_qgc.sh
```

`setup_qgc.sh` розпаковує AppImage і з пакетів Ubuntu 24.04 (libc6 2.39, libstdc++6 14.2, libgcc-s1) готує каталог
`glibc239`: QGC v5.1.5 зібрано під glibc >= 2.38, а у VM Ubuntu 22.04 (glibc 2.35). QGC запускається через
завантажувач `ld-linux` цих бібліотек без sudo і без зміни системних.

З Mac скрипти копіюються у VM командою `./deploy.sh`.

## Запуск

| Дія | Команда (у VM) |
|---|---|
| Gazebo (без вікна) + SITL + MAVProxy | `~/lab7/scripts/start_sim.sh` |
| QGroundControl на дисплеї :97 + VNC | `~/lab7/scripts/start_qgc.sh` |
| План місії варіанта | `python3 ~/lab7/tools/make_plan.py ~/lab7/variant.env <файл.plan>` |
| Вікно Gazebo (для знімків) | `~/lab7/scripts/start_gui.sh`, `stop_gui.sh` |
| Зупинка | `~/lab7/scripts/stop_qgc.sh`, `~/lab7/scripts/stop_sim.sh` |

Порядок важливий: спочатку `start_sim.sh`, потім `start_qgc.sh`. Перезапуск SITL під запущеним QGC обриває
з'єднання, і QGC може впасти.

`start_sim.sh` запускає три незалежні процеси: `gz sim -s`, `arducopter --model json` і MAVProxy
(`--out 127.0.0.1:14550` для QGC, `--out 127.0.0.1:14551` для скриптів). За замовчуванням у світ підставляється
модель `iris_with_ardupilot` без гімбала і камери (`start_sim.sh gimbal` - стандартна `iris_with_gimbal`): у VM
немає GPU, камера рендериться на CPU і знижує темп симуляції приблизно до 0.4-0.5 від реального, а CSV QGC
пишеться за годинником реального часу. Без камери темп 1.00.

## Результат варіанта 5

| Показник | Значення |
|---|---|
| Набір висоти | 50 м за 24 с (2.5 м/с) |
| Найбільша висота | 50.0 м (CSV), 50.02 м (.tlog) |
| Найбільша швидкість | 5.0 м/с наземна й повітряна |
| Час польоту | 114 с (QGC, arm -> disarm) |
| Початкова координата | -35.3632621; 149.1652374 |
| Кінцева координата | -35.3631166; 149.1639735 (збігається з ціллю) |
| Максимальний roll | 5.0 градуса (CSV, 1 Гц), 5.29 (.tlog) |
| Режими | Stabilize -> Guided -> Auto |

Файли: `results/telemetry/*.tlog` і `*.csv` (QGC), `results/variant5.plan`, `results/analysis/` (графіки висоти,
повітряної та наземної швидкостей, траєкторії і `metrics_csv.json`), `results/telemetry/tlog_summary.json`.

## Аналіз

```bash
python3 tools/analyze_csv.py variant.env "results/telemetry/<файл>.csv" results/analysis
python3 tools/analyze_tlog.py "<файл>.tlog" results/telemetry/tlog_summary.json
```

`analyze_tlog.py` запускається у VM (потрібен pymavlink). CSV QGC не містить режиму польоту й стану arm, їх беруть з
`.tlog`.

## Відхилення від методички

- `WPNAV_SPEED` у ArduCopter V4.8.0-dev немає, його замінює `WP_SPD` в м/с: `WPNAV_SPEED = 100 * V = 500 см/с`
  відповідає `WP_SPD = 5`.
- Модель дрона без камери гімбала (причина вище), світ і стартова точка стандартні.
- Налаштування журналів у QGC 5.1 лежать у Telemetry -> Logging; каталог журналів `~/lab7/logs/qgc_data`.
- `.tlog` QGC записує в каталог під час наступного запуску програми.
- Автопілот роздармовує апарат через `DISARM_DELAY = 10` с без зльоту, тому arm і Start Mission виконуються підряд.

## Структура

```
variant.env           параметри варіанта і перерахунок швидкості
deploy.sh             копіювання скриптів на VM
config/               додаткові початкові параметри SITL (DDS_ENABLE 0)
gui/                  конфіг вікна Gazebo
scripts/              запуск і зупинка Gazebo+SITL, QGC, вікна Gazebo, знімки екрана
tools/                план місії, запис MAVLink, аналіз .tlog і CSV
results/              телеметрія, план, графіки
```
