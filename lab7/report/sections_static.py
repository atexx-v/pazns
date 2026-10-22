import docx_style as s

TITLE = ("Інтеграція телеметрії та протоколу MAVLink. Налаштування і перевірка обміну даними між "
         "безпілотною системою та наземною станцією керування.")

GOAL = ("Набуття практичних навичок розгортання програмного середовища для моделювання безпілотної "
        "авіаційної системи, налаштування обміну MAVLink між ArduPilot SITL і наземною станцією "
        "QGroundControl, виконання автоматичної місії та збереження й аналізу телеметричних даних польоту.")

def task(doc, v):
    s.text(doc, (f"Варіант {v['variant']} (таблиця 7.6 методички). Номер варіанта для групи ІР-33 дорівнює "
                 "порядковому номеру студента в журналі. Параметри індивідуального завдання наведено в таблиці 1."))
    s.table(doc, [
        ["Параметр", "Позначення", "Одиниця", "Значення"],
        ["Висота зльоту", "H", "м", f"{v['alt']:g}"],
        ["Горизонтальна швидкість", "V", "м/с", f"{v['speed']:g}"],
        ["Цільова точка, широта", "latitude", "градуси WGS 84", f"{v['lat']}"],
        ["Цільова точка, довгота", "longitude", "градуси WGS 84", f"{v['lon']}"],
        ["Параметр ArduCopter WPNAV_SPEED", "100 · V", "см/с", f"{v['speed'] * 100:g}"],
    ], [3600, 1900, 2200, 1938], caption="Таблиця 1 – Параметри індивідуального завдання (варіант 5)")
    s.text(doc, ("Необхідно розгорнути Gazebo Sim, ArduPilot SITL і QGroundControl, налаштувати збереження "
                 "журналів телеметрії (.tlog і .csv), створити в QGroundControl місію Takeoff – Waypoint – Land, "
                 "виконати її в автоматичному режимі, після посадки проаналізувати CSV-файл, заповнити таблицю "
                 "показників польоту, побудувати три графіки (висота, повітряна і наземна швидкості від часу) і "
                 "пояснити призначення щонайменше трьох MAVLink-повідомлень."))

def environment(doc, env_rows):
    s.subheading(doc, "1. Середовище та програмне забезпечення")
    s.text(doc, ("Gazebo Sim, ArduPilot SITL і QGroundControl працюють у віртуальній машині Ubuntu 22.04 aarch64, "
                 "створеній у UTM на Mac з процесором Apple Silicon. Така архітектура дозволяє запускати все "
                 "програмне забезпечення без емуляції набору інструкцій. Для QGroundControl використано "
                 "офіційну збірку для Linux aarch64; вікно програми відображається на віртуальному дисплеї Xvfb "
                 "і транслюється по VNC. Версії всіх компонентів наведено в таблиці 2."))
    s.table(doc, env_rows, [3000, 6638], caption="Таблиця 2 – Операційна система та програмне забезпечення")
    s.text(doc, ("Сумісність версій перевірено практично: QGroundControl v5.1.5 отримує HEARTBEAT від "
                 "ArduCopter V4.8.0-dev, визначає тип апарата «мультиротор», отримує параметри і передає "
                 "план місії; Gazebo Harmonic працює з плагіном ardupilot_gazebo через JSON-інтерфейс SITL."))

DEPLOY_COMMANDS = """vishnevskiy@vishnevskiy:~$ mkdir -p ~/lab7/qgc && cd ~/lab7/qgc
vishnevskiy@vishnevskiy:~/lab7/qgc$ curl -L -C - --retry 20 -o QGroundControl-aarch64.AppImage \\
    https://github.com/mavlink/qgroundcontrol/releases/download/v5.1.5/QGroundControl-aarch64.AppImage
vishnevskiy@vishnevskiy:~/lab7/qgc$ ~/lab7/scripts/setup_qgc.sh"""

START_COMMANDS = """vishnevskiy@vishnevskiy:~$ ~/lab7/scripts/start_sim.sh
vishnevskiy@vishnevskiy:~$ ~/lab7/scripts/start_qgc.sh
vishnevskiy@vishnevskiy:~$ python3 ~/lab7/tools/make_plan.py ~/lab7/variant.env ~/lab7/variant5.plan
vishnevskiy@vishnevskiy:~$ ~/lab7/scripts/stop_qgc.sh
vishnevskiy@vishnevskiy:~$ ~/lab7/scripts/stop_sim.sh"""

SCRIPTS_ROWS = [
    ["Файл", "Призначення"],
    ["variant.env", "Параметри варіанта (H, V, ціль) і перерахунок WPNAV_SPEED = 100 · V."],
    ["scripts/env.sh", "Спільне середовище: ROS 2 Humble, Gazebo Harmonic, шляхи до ардупілотних пакетів, каталоги журналів."],
    ["scripts/start_sim.sh", "Запускає Gazebo-сервер зі світом runway, ArduPilot SITL і MAVProxy; чекає готовності автопілота."],
    ["scripts/wait_ready.py", "Через pymavlink слухає службовий порт 14551 і чекає біт PREARM_CHECK у SYS_STATUS."],
    ["scripts/setup_qgc.sh", "Розпаковує AppImage QGroundControl і перевіряє залежності, друкує SHA-256."],
    ["scripts/start_qgc.sh", "Запускає Xvfb :97, QGroundControl і VNC на порту 5901."],
    ["scripts/stop_sim.sh, stop_qgc.sh", "Зупиняють усі процеси лаби й чистять залишки Fast DDS."],
    ["scripts/start_gui.sh, stop_gui.sh", "Вікно Gazebo на дисплеї :98 з трансляцією по VNC, камера переходить до моделі дрона."],
    ["scripts/capture_frames.sh", "Знімки віртуального екрана кожні 2 с для скриншотів початку й кінця польоту."],
    ["tools/make_plan.py", "Формує план місії .plan за variant.env (Takeoff, Waypoint, Land)."],
    ["tools/mav_recorder.py", "Незалежний запис MAVLink (10 Гц) для перехресної перевірки CSV."],
    ["tools/analyze_tlog.py", "Розбір .tlog: режими, arm/disarm, службові повідомлення, максимуми."],
    ["tools/analyze_csv.py", "Рахує показники таблиці 7.4 за CSV QGroundControl і будує графіки."],
    ["tools/build_xlsx.py", "Збирає Excel-файл: вихідний CSV, виділений політ, таблиця 7.4 формулами, діаграми."],
]

MAVLINK_ROWS = [
    ["Повідомлення", "Призначення", "Що показує QGroundControl"],
    ["HEARTBEAT",
     "Періодичний сигнал присутності апарата (1 Гц). Містить тип апарата, тип автопілота, режим польоту "
     "(custom_mode) і прапорець arm у base_mode. За його появою QGC вирішує, що з'єднання встановлено.",
     "Тип «мультиротор», режим (Stabilize, Guided, Auto, Land), стан Armed/Disarmed."],
    ["GLOBAL_POSITION_INT",
     "Позиція, оцінена автопілотом: широта і довгота (градуси · 10⁷), висота над рівнем моря й відносно "
     "точки старту (мм), складові швидкості vx, vy, vz (см/с), курс.",
     "Положення на карті, відносна висота, наземна швидкість."],
    ["ATTITUDE",
     "Кути орієнтації апарата roll, pitch, yaw (рад) і кутові швидкості.",
     "Штучний горизонт, значення крену й тангажа; з нього отримано максимальний roll."],
    ["SYS_STATUS",
     "Стан бортових систем: які датчики присутні, ввімкнені й справні, напруга (мВ), струм (сА), залишок "
     "заряду батареї (%). Біт PREARM_CHECK показує, що автопілот пройшов передпольотні перевірки.",
     "Індикатор батареї й повідомлення про готовність до arm."],
    ["GPS_RAW_INT",
     "Сирі дані GNSS-приймача: тип фіксації (fix_type), кількість видимих супутників, координати, HDOP.",
     "Індикатор GPS: тип fix і кількість супутників."],
    ["VFR_HUD",
     "Дані для індикаторів пілота: повітряна швидкість (airspeed), наземна швидкість (groundspeed), "
     "висота, швидкість підйому, курс і газ.",
     "Швидкості та висота в панелі приладів; джерело графіків повітряної і наземної швидкості."],
]
