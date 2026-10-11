# Програмно-апаратне забезпечення систем рухомих об'єктів

Вишневський Артем, ІР-33. Лабораторні роботи №2 і №9, варіант 5.

## Структура

```
lab2/                                 Gazebo + ArduPilot SITL + ROS 2: політ дрона до точки з автопосадкою
├── fpv_lab2/                         ROS 2 пакет (Python)
│   ├── fpv_lab2/flight_test/         приклад викладача: зліт, зависання, посадка (без змін)
│   ├── fpv_lab2/goto_target/         власний алгоритм польоту до цілі
│   │   ├── navigator.py              ціль, швидкість і похибка
│   │   ├── goto_handler.py           фази: набір висоти, стабілізація, політ, підтвердження, посадка
│   │   ├── goto_target_node.py       ROS 2 вузол: одометрія і команди швидкості
│   │   └── main.py                   точка входу
│   ├── package.xml, setup.py,        опис і збірка пакета
│   │   setup.cfg, resource/
│   └── LICENSE
├── scripts/
│   ├── env.sh                        середовище ROS 2 і Gazebo
│   ├── start_sim.sh                  запуск симуляції без вікна, чекає готовності дрона
│   ├── run_example.sh                приклад викладача
│   ├── run_goto.sh                   політ до цілі свого варіанта
│   ├── start_gui.sh                  вікна Gazebo (і RViz) по VNC
│   ├── stop_gui.sh                   зупинка вікон
│   └── stop_sim.sh                   зупинка симуляції
├── gui/
│   ├── live.config                   вікно Gazebo: лише 3D-сцена
│   └── full.config                   вікно Gazebo: повний інтерфейс
└── variant.env                       параметри варіанта

lab9/                                 кріплення VTX
├── f3d/lab9_vishnevskyi.f3d          модель Fusion (Git LFS)
└── stl/vtx_case.stl                  модель для друку
```

## Лабораторна 2

Середовище: Ubuntu 22.04, ROS 2 Humble, Gazebo Harmonic, ArduPilot SITL.

Варіант 5: Δx = 7.0, Δy = −0.1. Ціль: `x_target = x0 − Δx`, `y_target = y0 − Δy`. Допуск 0.25 м. Осі дзеркальні (`FRAME_SIGN=-1.0` у `variant.env`).

Результат: похибка перед посадкою 0.11 м.

Збірка пакета:

```bash
cd ~/fpv_labs && colcon build --symlink-install --packages-select fpv_lab2
```

Запуск (папка `lab2/` лежить у `~/lab2`):

```bash
~/lab2/scripts/start_sim.sh
~/lab2/scripts/run_goto.sh
~/lab2/scripts/stop_sim.sh
```

`start_sim.sh` закінчується рядком «Готово», після нього можна запускати політ. Вікна по VNC: `~/lab2/scripts/start_gui.sh rviz`, підключення `vnc://<IP VM>:5900`.
