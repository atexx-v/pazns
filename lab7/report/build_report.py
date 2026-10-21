import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import docx_style as s
import sections_static as st

SHOTS = os.path.join(ROOT, "results", "screenshots")
PLOTS = os.path.join(ROOT, "results", "analysis")
OUT = os.path.join(ROOT, "lab7_vishnevskiy_ir33.docx")

M = json.load(open(os.path.join(PLOTS, "metrics_csv.json"), encoding="utf-8"))
T = json.load(open(os.path.join(ROOT, "results", "telemetry", "tlog_summary.json"), encoding="utf-8"))
V = {"variant": 5, "alt": 50, "speed": 5, "lat": "-35.3631166", "lon": "149.1639735"}

def fmt(x, nd=1):
    return ("%." + str(nd) + "f") % x

def read(rel):
    return open(os.path.join(ROOT, rel), encoding="utf-8").read().rstrip("\n")

def code_files(doc, rel, caption, size=6.5, chunk=46):
    s.para(doc, caption, 12, italic=True, before=60, after=40, keep_next=True)
    lines = read(rel).split("\n")
    for i in range(0, len(lines), chunk):
        s.code_block(doc, "\n".join(lines[i:i + chunk]), size)

fig_no = [0]
FIG = {}

def figure(doc, key, path, width, caption):
    fig_no[0] += 1
    FIG[key] = fig_no[0]
    s.figure(doc, path, width, "Рисунок %d – %s" % (fig_no[0], caption))

def build():
    doc = s.new_document()
    s.title_page(doc, 7, os.path.join(ROOT, "assets", "logo_lpnu.png"))

    s.heading(doc, "НАЗВА:")
    s.text(doc, st.TITLE)
    s.heading(doc, "МЕТА:")
    s.text(doc, st.GOAL)
    s.heading(doc, "ЗАВДАННЯ:")
    st.task(doc, V)

    s.heading(doc, "РЕАЛІЗАЦІЯ:")

    env_rows = [
        ["Компонент", "Версія / параметри"],
        ["Хост", "MacBook Air, Apple M2 (arm64), 16 ГБ RAM"],
        ["ОС хоста", "macOS 27.0.1, архітектура arm64"],
        ["Віртуалізація", "UTM 4.7.5; віртуальна машина: 4 ядра, 6 ГБ RAM"],
        ["ОС у віртуальній машині (тут працюють усі компоненти)", "Ubuntu 22.04.5 LTS, ядро 5.15.0-198-generic, архітектура aarch64"],
        ["Gazebo Sim", "8.15.0 (Harmonic), світ iris_runway зі складу ardupilot_gazebo (коміт cc0290d)"],
        ["ArduPilot SITL", "ArduCopter V4.8.0-dev, коміт 665c0dee (від 18.09.2026)"],
        ["Міст Gazebo – SITL", "плагін ArduPilotPlugin (ardupilot_gazebo, коміт cc0290d), бекенд SITL --model json"],
        ["MAVProxy", "1.8.74"],
        ["QGroundControl", "v5.1.5 64 bit, QGroundControl-aarch64.AppImage, SHA-256 ddd92fe3…2c91e03"],
        ["Бібліотеки для запуску QGC", "libc6 2.39, libstdc++6 14.2.0, libgcc-s1 14.2.0 з Ubuntu 24.04 (3 пакети .deb)"],
        ["Допоміжне ПЗ", "Python 3.10.12, pymavlink 2.4.49 (у VM); Python 3.9, matplotlib 3.9.4 (аналіз на Mac)"],
    ]
    st.environment(doc, env_rows)

    s.subheading(doc, "2. Розгортання середовища (завдання 1)")
    s.text(doc, ("Спосіб розгортання обрано самостійно: локальне встановлення у віртуальній машині без Docker. "
                 "Gazebo Harmonic, ArduPilot SITL і робочий простір ros2_ws розгорнуто раніше для лабораторної №2 "
                 "за офіційними інструкціями, тому тут повторно використано бінарник arducopter, плагін ardupilot_gazebo "
                 "і набір світів. ROS 2 у цій роботі не використовується. Нове в цій роботі – наземна станція "
                 "QGroundControl і скрипти швидкого запуску."))
    s.text(doc, "Завантаження QGroundControl і одноразова підготовка:")
    s.code_block(doc, st.DEPLOY_COMMANDS)
    s.text(doc, ("Особливість: QGroundControl v5.1.5 зібрано під Ubuntu 24.04 і він вимагає glibc не нижче 2.38 та "
                 "libstdc++ з GLIBCXX_3.4.32, тоді як у VM Ubuntu 22.04 (glibc 2.35). Системні бібліотеки без sudo не оновити, "
                 "тому три пакети з архіву Ubuntu 24.04 розпаковано в окремий каталог без встановлення, а QGroundControl "
                 "запускається через їхній завантажувач ld-linux (див. setup_qgc.sh). Решта програм у системі використовує "
                 "рідні бібліотеки. Вікно QGroundControl відображається на віртуальному дисплеї Xvfb і транслюється по VNC."))
    s.text(doc, ("Ще одне рішення для швидкості симуляції: у VM немає GPU-прискорення, тому камера гімбала стандартної моделі "
                 "iris_with_gimbal рендериться на CPU і знижує темп симуляції приблизно до 0,4–0,5 від реального часу (виміряно за відношенням sim_time до real_time у Gazebo). "
                 "Файл CSV QGroundControl пишеться за годинником реального часу, тому такий темп спотворив би часову вісь. "
                 "Скрипт start_sim.sh за замовчуванням підставляє у світ iris_runway.sdf модель iris_with_ardupilot (той самий "
                 "дрон без гімбала і камери); смуга, рельєф, фізика, стартова точка і керування не змінюються. "
                 "Виміряний темп симуляції в цьому режимі дорівнює 1,00 від реального. Режим зі стандартною моделлю "
                 "лишається доступним: start_sim.sh gimbal."))
    s.subheading(doc, "Скрипти швидкого запуску")
    s.text(doc, ("Створено набір bash-скриптів і допоміжних програм, які запускають усі компоненти без ручного введення "
                 "команд. Призначення файлів наведено в таблиці 3, повні тексти основних скриптів – нижче."))
    s.table(doc, st.SCRIPTS_ROWS, [3000, 6638], caption="Таблиця 3 – Призначення скриптів і файлів")
    s.text(doc, "Команди запуску і зупинки (виконуються у VM):")
    s.code_block(doc, st.START_COMMANDS)
    s.text(doc, ("start_sim.sh запускає три незалежні процеси, як у документації ArduPilot «SITL with Gazebo»: Gazebo-сервер "
                 "(gz sim -s, без вікна), arducopter (--model json) і MAVProxy. MAVProxy бере TCP-порт 5760 у SITL і роздає "
                 "MAVLink по UDP на 127.0.0.1:14550 (туди слухає QGroundControl, автопідключення UDP за замовчуванням) та "
                 "127.0.0.1:14551 (службовий порт для скриптів). Скрипт завершується, коли автопілот пройшов передпольотні "
                 "перевірки (біт PREARM_CHECK у SYS_STATUS), це видно за рядком «Готово»."))
    code_files(doc, "variant.env", "variant.env (параметри варіанта)")
    code_files(doc, "scripts/env.sh", "env.sh")
    code_files(doc, "scripts/start_sim.sh", "start_sim.sh")
    code_files(doc, "scripts/start_qgc.sh", "start_qgc.sh")
    code_files(doc, "scripts/setup_qgc.sh", "setup_qgc.sh")
    code_files(doc, "scripts/wait_ready.py", "wait_ready.py")
    code_files(doc, "config/sitl_lab7.parm", "config/sitl_lab7.parm (додаткові початкові параметри SITL)")
    s.text(doc, ("Файл sitl_lab7.parm потрібен через збірку arducopter з ROS 2: DDS у ній увімкнено, і без агента micro-ROS "
                 "процес завершується повідомленням «DDS: No ping response, exiting». Для роботи з MAVLink DDS не потрібен."))
    s.subheading(doc, "Перевірка: QGroundControl виявляє апарат")
    s.text(doc, ("Після запуску start_sim.sh і start_qgc.sh QGroundControl автоматично встановив з'єднання: у верхній панелі "
                 "з'явився стан «Ready», режим Stabilize, 10 супутників GPS, заряд батареї 100 %%, а на карті – апарат "
                 "на аеродромі CMAC (рис. %d). Підключення визначається за повідомленнями HEARTBEAT апарата "
                 "(тип 2 – квадрокоптер, автопілот 3 – ArduPilotMega)." % (fig_no[0] + 1)))
    figure(doc, "connected", os.path.join(SHOTS, "02_qgc_connected.png"), 15.5,
           "QGroundControl виявив апарат: стан «Ready», режим Stabilize, 10 супутників GPS")

    s.subheading(doc, "3. Налаштування QGroundControl і запису телеметрії (завдання 2)")
    s.text(doc, ("У QGroundControl v5.1.5 розташування параметрів відрізняється від тексту методички: шлях збереження "
                 "задається в Application Settings → General, а перемикачі журналів телеметрії лежать в окремому розділі "
                 "Application Settings → Telemetry → Logging. Виконано такі дії:"))
    s.bullet(doc, ("Application Load/Save Path змінено зі стандартного ~/Documents/QGroundControl на каталог лабораторної "
                   "/home/vishnevskiy/lab7/logs/qgc_data (рис. %d). Відтепер там створюються підкаталоги Telemetry, Missions, "
                   "Parameters та інші." % (fig_no[0] + 1)))
    s.bullet(doc, ("У блоці Logging перемикач «Save log after each flight» уже був увімкнений за замовчуванням, а «Save CSV log "
                   "of telemetry data» (запис усіх параметрів апарата в CSV з частотою 1 Гц під час польоту) вимкнений; "
                   "його увімкнено (рис. %d)." % (fig_no[0] + 2)))
    figure(doc, "path", os.path.join(SHOTS, "03_settings_save_path.png"), 12.5,
           "Application Settings → General: Application Load/Save Path = /home/vishnevskiy/lab7/logs/qgc_data")
    figure(doc, "logging", os.path.join(SHOTS, "04_settings_telemetry_logging.png"), 12.5,
           "Application Settings → Telemetry → Logging: увімкнено Save log after each flight і Save CSV log")
    s.text(doc, ("Далі відкрито Analyze Tools → MAVLink Inspector. Усі потрібні повідомлення надходять від автопілота "
                 "з частотою близько 4 Гц (HEARTBEAT – 1 Гц): HEARTBEAT (рис. %d), GLOBAL_POSITION_INT (рис. %d), "
                 "ATTITUDE (у списку зліва) та SYS_STATUS (рис. %d). У списку також видно GPS_RAW_INT, VFR_HUD, "
                 "HOME_POSITION, MISSION_CURRENT та інші."
                 % (fig_no[0] + 1, fig_no[0] + 2, fig_no[0] + 3)))
    figure(doc, "hb", os.path.join(SHOTS, "05a_inspector_heartbeat.png"), 15.5,
           "MAVLink Inspector: HEARTBEAT (type = 2, autopilot = 3, custom_mode = 3, base_mode = 89)")
    figure(doc, "gp", os.path.join(SHOTS, "05b_inspector_global_position.png"), 15.5,
           "MAVLink Inspector: GLOBAL_POSITION_INT (після посадки lat = -353631166, lon = 1491639735)")
    figure(doc, "ss", os.path.join(SHOTS, "05c_inspector_sys_status.png"), 15.5,
           "MAVLink Inspector: SYS_STATUS (voltage_battery = 12600 мВ, battery_remaining = 100 %)")
    s.text(doc, "Призначення основних повідомлень MAVLink, які надходять від автопілота, наведено в таблиці 4.")
    s.table(doc, st.MAVLINK_ROWS, [2600, 4600, 2438], caption="Таблиця 4 – Призначення MAVLink-повідомлень, що спостерігалися в Inspector")

    s.subheading(doc, "4. Підготовка та виконання місії (завдання 3)")
    s.text(doc, "Параметр швидкості. Методичка вимагає встановити WPNAV_SPEED = 100 · V = 500 см/с. Перевірка показала, що в "
                "цій збірці ArduCopter (V4.8.0-dev) такого параметра немає: у версіях 4.7 і новіших групу WPNAV_* перейменовано "
                "на WP_*, а швидкість задається параметром WP_SPD в метрах за секунду. На запит PARAM_REQUEST_READ параметри "
                "WPNAV_SPEED, WPNAV_ACCEL, WPNAV_SPEED_UP, WPNAV_RADIUS автопілот не відповідає, а WP_SPD, WP_ACC, WP_SPD_UP, "
                "WP_RADIUS_M відповідають. Еквівалент заданого значення: 500 см/с = 5 м/с, тому встановлено "
                "WP_SPD = 5.0 м/с (було 10.0 м/с). Значення змінено у Vehicle Setup → Parameters (рис. %d, %d) і підтверджено "
                "незалежним читанням з автопілота." % (fig_no[0] + 1, fig_no[0] + 2))
    figure(doc, "wp1", os.path.join(SHOTS, "06_param_wp_spd_edit.png"), 13.5,
           "Редагування параметра WP_SPD: введено значення 5 м/с")
    figure(doc, "wp2", os.path.join(SHOTS, "07_param_wp_spd_saved.png"), 13.5,
           "Група WP після збереження: WP_SPD = 5.0 m/s")

    s.text(doc, ("План місії складається з трьох елементів (таблиця 5). План сформовано скриптом make_plan.py за параметрами "
                 "variant.env у форматі .plan, який QGroundControl відкриває на вкладці Plan так само, як і створений вручну "
                 "(методичка допускає задання цілі окремим файлом плану місії QGroundControl). Висота Waypoint дорівнює "
                 "висоті зльоту, Land виконується в цільовій точці."))
    s.table(doc, [
        ["№", "Елемент плану", "Команда MAVLink", "Параметри"],
        ["1", "Takeoff", "NAV_TAKEOFF (22)", "висота 50 м (відносно точки старту)"],
        ["2", "Waypoint", "NAV_WAYPOINT (16)", "широта -35.3631166, довгота 149.1639735, висота 50 м"],
        ["3", "Land", "NAV_LAND (21)", "широта -35.3631166, довгота 149.1639735"],
    ], [600, 2100, 2500, 4438], caption="Таблиця 5 – Створений план місії (варіант 5)")
    figure(doc, "plan", os.path.join(SHOTS, "08a_plan_overview.png"), 15.5,
           "Вкладка Plan: план variant5 із елементами Takeoff, Waypoint, Land; довжина маршруту 115,7 м")
    figure(doc, "planpos", os.path.join(SHOTS, "08_plan_waypoint_position.png"), 15.5,
           "Waypoint: Edit Position (Latitude -35.3631166, Longitude 149.1639735) і Altitude (Rel) 50.0 м")
    s.text(doc, ("План передано в ArduPilot кнопкою Upload. Незалежна перевірка запитом MISSION_REQUEST_LIST: автопілот зберігає "
                 "4 елементи – точку home (seq 0) і три елементи плану з координатами й висотою з таблиці 5."))
    s.text(doc, ("Виконання. На вкладці Fly arm виконано з панелі статусу «Ready» утриманням кнопки Arm (у QGroundControl 5.1 "
                 "підтвердження дій робиться утриманням), одразу після цього – утриманням кнопки «Start Mission» (її підказка: "
                 "«Takeoff and start the current mission»). За потоком HEARTBEAT з .tlog QGroundControl виставив режим Guided, "
                 "виконав arm і перевів апарат у Auto, після чого автопілот виконував елементи плану: Takeoff, Waypoint "
                 "(«Reached command #2»), Land. Початок місії показано на рис. %d, завершення польоту – на рис. %d, "
                 "положення моделі в Gazebo після посадки – на рис. %d." % (fig_no[0] + 1, fig_no[0] + 2, fig_no[0] + 3)))
    figure(doc, "start", os.path.join(SHOTS, "09_mission_start_takeoff.png"), 15.5,
           "Початок місії: «Flying», режим Auto, набір висоти (9,2 м, 2,5 м/с), таймер польоту 00:00:07")
    figure(doc, "end", os.path.join(SHOTS, "10_flight_end_landed.png"), 15.5,
           "Завершення польоту: «Ready», апарат у цільовій точці, висота 0,0 м, час польоту 00:01:54, 115,7 м від точки старту")
    figure(doc, "gz", os.path.join(SHOTS, "11_gazebo_drone_at_target.png"), 13.0,
           "Gazebo Sim: модель iris_with_ardupilot у цільовій точці після посадки")

    ev = T["transitions"]
    s.text(doc, "Хронологія подій за .tlog (HEARTBEAT і STATUSTEXT апарата) наведена в таблиці 6.")
    s.table(doc, [
        ["Час, UTC", "Подія"],
        ["21:41:36", "перший arm (Stabilize); без команди на зліт автопілот сам роздармував апарат через DISARM_DELAY = 10 с (21:41:46)"],
        ["21:41:59", "режим Guided, arm; режим Auto; «Mission: 1 Takeoff»"],
        ["21:42:25", "завершено набір висоти 50 м, «Mission: 2 WP»"],
        ["21:42:53", "«Reached command #2» – досягнуто цільової точки, «Mission: 3 Land»"],
        ["21:43:24", "службове повідомлення «PrecLand: Failsafe Measures» (точна посадка не налаштована)"],
        ["21:43:54", "«Disarming motors» – апарат приземлився й роздармований у режимі Auto"],
    ], [1800, 7838], caption="Таблиця 6 – Хронологія польоту за .tlog")
    s.text(doc, ("Файли журналів у налаштованому каталозі /home/vishnevskiy/lab7/logs/qgc_data/Telemetry: "
                 "«2026-10-21 21-50-01.tlog» (5,2 МБ, потік MAVLink усієї сесії з польотом) і «2026-10-21 21-41-37 vehicle1.csv» "
                 "(CSV, 1 Гц, 196 стовпців). Обидва файли додаються до звіту. Зверніть увагу: QGroundControl записав .tlog "
                 "у каталог під час наступного запуску програми (так він завершує тимчасовий файл сесії), а CSV дописувався "
                 "до закриття програми, тому містить також рядки до і після польоту."))

    s.subheading(doc, "5. Аналіз телеметрії (завдання 4)")
    s.text(doc, ("CSV відкрито і оброблено скриптом analyze_csv.py на Python (CSV відкривається у будь-якому табличному "
                 "процесорі, але розрахунки й графіки зручніше відтворювати програмно). Спочатку виділено сам політ: від "
                 "останнього скидання лічильника flightTime (початок останнього arm) до дотику до землі, тобто {0} рядків із {1}. "
                 "Етапи визначено за даними: зліт – до досягнення 99 % заданої висоти, горизонтальний політ – поки наземна "
                 "швидкість не менша за 0,5 м/с на заданій висоті, посадка – від зупинки над ціллю до дотику. "
                 "CSV QGroundControl не містить режиму польоту й стану arm, тому ці два показники взято з .tlog "
                 "(скрипт analyze_tlog.py). Результати зведено в таблицю 7."
                 ).format(M["flight_rows"], M["csv_rows_total"]))

    rows74 = [
        ["Показник", "Значення"],
        ["Час зльоту", "arm і початок набору висоти о %s UTC; набір заданих 50 м за %s с" % (T["arm_utc"][11:], fmt(M["takeoff_phase_s"], 0))],
        ["Найбільша висота", "%s м (CSV); %s м за GLOBAL_POSITION_INT з .tlog" % (fmt(M["max_alt_m"]), fmt(T["max_rel_alt_m"], 2))],
        ["Найбільша швидкість", "%s м/с наземна, %s м/с повітряна (середня на сталій ділянці %s м/с)" % (
            fmt(M["max_groundspeed_ms"]), fmt(M["max_airspeed_ms"]), fmt(M["steady_groundspeed_ms"], 2))],
        ["Час польоту", "114 с за лічильником QGC (arm → disarm); дотик до землі на %s с; за .tlog arm → disarm %s с" % (
            fmt(M["flight_time_by_rows_s"], 0), fmt(T["flight_duration_s"]))],
        ["Початкова координата", "%s; %s" % (M["start"]["lat"], M["start"]["lon"])],
        ["Кінцева координата", "%s; %s (збігається із заданою)" % (M["end"]["lat"], M["end"]["lon"])],
        ["Максимальний roll", "%s° за CSV (1 Гц); %s° за ATTITUDE з .tlog" % (fmt(M["max_abs_roll_csv_deg"]), fmt(T["max_abs_roll_deg"], 2))],
        ["Режими польоту", "Stabilize → Guided → Auto (Takeoff, Waypoint і Land виконано в Auto)"],
        ["Стан arm до та після місії", "до: disarmed; під час польоту: armed (%s – %s UTC); після: disarmed" % (T["arm_utc"][11:], T["disarm_utc"][11:])],
    ]
    s.table(doc, rows74, [2900, 6738], caption="Таблиця 7 – Результати аналізу телеметрії (за формою таблиці 7.4)")

    s.text(doc, ("Графіки висоти, повітряної і наземної швидкостей від часу (рис. %d–%d) побудовано за CSV; етапи зльоту, "
                 "горизонтального польоту і посадки виділено кольором, пунктиром показано задані значення." % (
                     fig_no[0] + 1, fig_no[0] + 3)))
    figure(doc, "p_alt", os.path.join(PLOTS, "plot_altitude.png"), 16.0, "Висота від часу")
    figure(doc, "p_as", os.path.join(PLOTS, "plot_airspeed.png"), 16.0, "Повітряна швидкість від часу")
    figure(doc, "p_gs", os.path.join(PLOTS, "plot_groundspeed.png"), 16.0, "Наземна швидкість від часу")
    figure(doc, "p_tr", os.path.join(PLOTS, "plot_trajectory.png"), 16.0,
           "Траєкторія польоту за CSV у локальних координатах відносно точки старту")

    s.text(doc, "Порівняння заданих параметрів із фактичними даними наведено в таблиці 8.")
    s.table(doc, [
        ["Параметр", "Задано", "Фактично", "Відхилення"],
        ["Висота польоту H", "50 м", "50,0 м (CSV), 50,02 м (.tlog)", "0,0…0,02 м"],
        ["Горизонтальна швидкість V", "5 м/с (WP_SPD = 5.0)", "5,0 м/с, середня на сталій ділянці %s м/с" % fmt(M["steady_groundspeed_ms"], 2),
         "розгін і гальмування"],
        ["Цільова точка", "-35.3631166; 149.1639735", "%s; %s" % (M["end"]["lat"], M["end"]["lon"]), "< 0,1 м"],
        ["Відстань від точки старту до цілі", "–", "%s м за QGC, пройдено %s м" % (fmt(M["distance_home_target_m"]), fmt(M["flight_distance_m"])), "–"],
    ], [2700, 2300, 3100, 1538], caption="Таблиця 8 – Задані й фактичні параметри місії")
    s.text(doc, "Пояснення відхилень і особливостей графіків:")
    s.bullet(doc, ("Швидкість. Найбільша наземна швидкість (5,0 м/с) збігається із заданою, але до неї дрон розганяється приблизно "
                   "7 с (на графіку швидкість зростає з 0 до 5 м/с з 26-ї до 33-ї секунди), а в кінці гальмує. Причина – обмеження "
                   "прискорення автопілотом (WP_ACC = 2,5 м/с²); тому середня швидкість за весь горизонтальний етап менша за задану."))
    s.bullet(doc, ("Висота. Підйом триває з постійною швидкістю 2,5 м/с (WP_SPD_UP), завдяки чому 50 м досягається за %s с. "
                   "Незначне перевищення (0,02 м за .tlog) лежить у межах точності регулятора висоти." % fmt(M["takeoff_phase_s"], 0)))
    s.bullet(doc, ("Посадка. Зниження виконується зі швидкістю 1,5 м/с (WP_SPD_DN) до висоти 10 м (LAND_ALT_LOW_M), де є "
                   "площадка приблизно на 10 с, що збігається з повідомленням «PrecLand: Failsafe Measures»; потім швидкість "
                   "зниження зменшується до 0,5 м/с (LAND_SPD_MS) аж до дотику."))
    s.bullet(doc, ("Цільова точка. Місія завершується посадкою в тих самих координатах, тому остання позиція збігається з "
                   "заданою до сьомого знака після коми (< 0,1 м). У симуляції немає вітру (SIM_WIND_SPD = 0), а положення, які бачить автопілот, майже не мають шуму "
                   "(кінцеві координати в CSV стабільні й збігаються до 7-го знака), що пояснює таку точність; "
                   "реальний апарат дав би відхилення порядку метра."))
    s.bullet(doc, ("Повітряна швидкість. ArduCopter не має датчика повітряної швидкості, тому поле airSpeed є оцінкою автопілота; "
                   "за відсутності вітру воно майже збігається з наземною швидкістю (максимальна різниця в CSV – 0,4 м/с під час "
                   "розгону), тому графіки рис. %d і %d схожі." % (FIG["p_as"], FIG["p_gs"])))
    s.bullet(doc, ("Roll. Найбільший крен 5,0° за CSV і 5,29° за ATTITUDE з .tlog (CSV фіксує лише одне значення за секунду, "
                   "тому пік повного потоку трохи вищий); найбільший тангаж 13,3° припадає на розгін і гальмування."))
    s.text(doc, ("Якість телеметрії. Потік MAVLink стабільний: частота повідомлень 4 Гц (HEARTBEAT – 1 Гц), без втрат "
                 "(drop_rate_comm = 0, errors_comm = 0 у SYS_STATUS), GPS: тип фіксації 6, 10 супутників, HDOP 1,2. "
                 "Обмеження CSV: частота 1 Гц, тому короткі процеси (розгін, гальмування) відображаються кількома точками; "
                 "напруга батареї (12,6 В) і заряд (100 %) за весь політ не змінюються, бо модель батареї SITL не розряджається. "
                 "Для детального аналізу використано .tlog (повна частота ATTITUDE, GLOBAL_POSITION_INT)."))

    s.subheading(doc, "6. Відхилення від методички та особливості виконання")
    for item in (
        "Параметр WPNAV_SPEED у ArduCopter V4.8.0-dev відсутній, його замінює WP_SPD (м/с): задано WP_SPD = 5 м/с, що відповідає WPNAV_SPEED = 500 см/с.",
        "У Gazebo використано модель iris_with_ardupilot (без камери гімбала) у стандартному світі iris_runway: світ і стартову точку не змінено, замінено лише модель дрона; причина – продуктивність без GPU (темп 1,00 замість ≈0,4–0,5).",
        "QGroundControl запущено у Linux-VM на віртуальному дисплеї, а не нативно на Mac: офіційна збірка aarch64 вимагає нових бібліотек, які підкладено окремо (setup_qgc.sh).",
        "Каталог журналів – /home/vishnevskiy/lab7/logs/qgc_data замість прикладу /logs (у прикладі потрібні права root).",
        "Перемикачі журналів у QGroundControl 5.1 знаходяться в Telemetry → Logging, а не в General.",
        "План місії створено скриптом у форматі .plan і відкрито в QGroundControl; Upload, перегляд і перевірка виконано в графічному інтерфейсі.",
        "CSV не містить режиму й стану arm, ці показники взято з .tlog; .tlog записано QGroundControl під час наступного запуску.",
        "Перший arm (21:41:36) автопілот скасував через 10 с, бо зліт не було запущено (DISARM_DELAY = 10 с); тому arm і Start Mission виконано послідовно без паузи. Окрема спроба «disarm» у польоті була відхилена автопілотом (повідомлення Arm/Disarm failed у QGroundControl), політ не переривався.",
        "Розрахунки й графіки виконано скриптом на Python замість табличного процесора.",
    ):
        s.bullet(doc, item)

    s.subheading(doc, "Додатки")
    s.text(doc, "До звіту додаються файли телеметрії та результатів:")
    s.bullet(doc, "2026-10-21 21-50-01.tlog – журнал MAVLink сесії QGroundControl, збережений у каталозі Telemetry;")
    s.bullet(doc, "2026-10-21 21-41-37 vehicle1.csv – CSV телеметрії з частотою 1 Гц;")
    s.bullet(doc, "variant5.plan – план місії у форматі QGroundControl;")
    s.bullet(doc, "tlog_summary.json, metrics_csv.json – результати розбору .tlog і CSV;")
    s.bullet(doc, "скрипти і конфігурації: репозиторій https://github.com/atexx-v/pazns, папка lab7.")

    s.heading(doc, "ВИСНОВКИ:")
    s.text(doc, ("У роботі розгорнуто відтворюване середовище Gazebo Sim, ArduPilot SITL і QGroundControl, налаштовано обмін "
                 "MAVLink між автопілотом і наземною станцією та виконано автоматичну місію за варіантом 5: зліт на 50 м, політ "
                 "до точки (-35.3631166; 149.1639735) зі швидкістю 5 м/с і посадка. Усі параметри місії виконано: найбільша висота "
                 "50,0 м, найбільша швидкість 5,0 м/с, кінцева координата збігається із цільовою, час польоту 114 с, апарат "
                 "після посадки автоматично роздармований."))
    s.text(doc, ("Практично перевірено, як працює MAVLink: за HEARTBEAT QGroundControl визначає наявність апарата, його тип і режим; "
                 "GLOBAL_POSITION_INT, ATTITUDE, VFR_HUD і SYS_STATUS дають позицію, орієнтацію, швидкості й стан систем; наземна "
                 "станція передає параметри (WP_SPD) і точки місії (MISSION_ITEM_INT), а автопілот підтверджує їх. "
                 "Збережено .tlog (повний потік повідомлень) і CSV (1 Гц, зручний для таблиць), їх можливості доповнюють "
                 "одна одну: у CSV немає режиму й arm, а .tlog не такий зручний для швидкого аналізу."))
    s.text(doc, ("Телеметрія якісна й узгоджена із завданням, але має обмеження симуляції: немає вітру і шуму GPS, тому точність "
                 "виходу в ціль нетипово висока, батарея не розряджається, а повітряна швидкість лише оцінюється. Окремі "
                 "відхилення від методички (параметр WP_SPD замість WPNAV_SPEED, модель дрона без камери, запуск QGroundControl "
                 "у VM) пояснені в розділі 6."))
    doc.save(OUT)
    print("Звіт збережено:", OUT)

if __name__ == "__main__":
    build()
