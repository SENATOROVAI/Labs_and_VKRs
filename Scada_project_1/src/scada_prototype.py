"""
Демонстрационный прототип SCADA-системы мониторинга
воздушной линии 6-10 кВ.

Функции:
- имитация датчиков тока и напряжения
- сбор и отображение параметров
- аварийная сигнализация при выходе за допустимые пределы
- ведение журнала событий
"""

import random
import time
import datetime


# ---------------------------------------------------------------------------
# Уставки (допустимые диапазоны)
# ---------------------------------------------------------------------------
CURRENT_WARNING = 350.0   # А — предупреждение
CURRENT_ALARM   = 400.0   # А — авария (перегрузка)
VOLTAGE_MIN     = 5.5     # кВ — нижняя граница напряжения
VOLTAGE_MAX     = 11.0    # кВ — верхняя граница напряжения
NOMINAL_VOLTAGE = 10.0    # кВ — номинальное напряжение линии

# Число секций (участков) линии
SECTIONS = 3

# ---------------------------------------------------------------------------
# Журнал событий
# ---------------------------------------------------------------------------
event_log: list[dict] = []


def log_event(section: int, event_type: str, message: str) -> None:
    """Записывает событие в журнал и выводит на экран."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = {
        "time": timestamp,
        "section": section,
        "type": event_type,
        "message": message,
    }
    event_log.append(entry)
    prefix = {
        "INFO":    "[  OK  ]",
        "WARNING": "[ WARN ]",
        "ALARM":   "[ALARM ]",
    }.get(event_type, "[......] ")
    print(f"  {prefix} {timestamp}  Секция {section}: {message}")


# ---------------------------------------------------------------------------
# Имитация датчиков
# ---------------------------------------------------------------------------
def simulate_current(section: int, cycle: int) -> float:
    """
    Возвращает имитированное значение тока для секции.
    Каждые 10 циклов в одной из секций создаётся нештатная ситуация.
    """
    base = 180.0 + section * 15.0
    noise = random.uniform(-10.0, 10.0)

    # Имитация перегрузки: в 5-м цикле — секция 2, в 10-м — секция 1
    if cycle == 5 and section == 2:
        return 420.0 + noise          # авария
    if cycle == 8 and section == 1:
        return 360.0 + noise          # предупреждение
    return base + noise


def simulate_voltage(section: int, cycle: int) -> float:
    """
    Возвращает имитированное значение напряжения для секции (кВ).
    На 7-м цикле в секции 3 моделируется провал напряжения.
    """
    base = NOMINAL_VOLTAGE
    noise = random.uniform(-0.2, 0.2)

    if cycle == 7 and section == 3:
        return 4.8 + noise            # провал ниже нормы
    return base + noise


# ---------------------------------------------------------------------------
# Проверка уставок
# ---------------------------------------------------------------------------
def check_current(section: int, current: float) -> None:
    if current >= CURRENT_ALARM:
        log_event(section, "ALARM",
                  f"ПЕРЕГРУЗКА: ток {current:.1f} А >= {CURRENT_ALARM} А")
    elif current >= CURRENT_WARNING:
        log_event(section, "WARNING",
                  f"Предупреждение: ток {current:.1f} А >= {CURRENT_WARNING} А")
    else:
        log_event(section, "INFO",
                  f"Ток в норме: {current:.1f} А")


def check_voltage(section: int, voltage: float) -> None:
    if voltage < VOLTAGE_MIN:
        log_event(section, "ALARM",
                  f"ПРОВАЛ НАПРЯЖЕНИЯ: {voltage:.2f} кВ < {VOLTAGE_MIN} кВ")
    elif voltage > VOLTAGE_MAX:
        log_event(section, "ALARM",
                  f"ПЕРЕНАПРЯЖЕНИЕ: {voltage:.2f} кВ > {VOLTAGE_MAX} кВ")
    else:
        log_event(section, "INFO",
                  f"Напряжение в норме: {voltage:.2f} кВ")


# ---------------------------------------------------------------------------
# Цикл опроса (имитация работы RTU + SCADA-сервера)
# ---------------------------------------------------------------------------
def run_scada(cycles: int = 10, poll_interval: float = 1.0) -> None:
    print("=" * 65)
    print("  SCADA-система мониторинга ВЛ 6-10 кВ  |  Прототип v1.0")
    print("=" * 65)
    print(f"  Число секций: {SECTIONS}  |  Цикл опроса: {poll_interval} с")
    print(f"  Уставки: I_warn={CURRENT_WARNING} А, I_alarm={CURRENT_ALARM} А")
    print(f"           U_min={VOLTAGE_MIN} кВ, U_max={VOLTAGE_MAX} кВ")
    print("=" * 65)

    for cycle in range(1, cycles + 1):
        print(f"\n--- Цикл опроса № {cycle} ---")

        for section in range(1, SECTIONS + 1):
            current = simulate_current(section, cycle)
            voltage = simulate_voltage(section, cycle)

            check_current(section, current)
            check_voltage(section, voltage)

        time.sleep(poll_interval)

    print("\n" + "=" * 65)
    print("  Работа системы завершена.")
    print(f"  Всего событий в журнале: {len(event_log)}")
    alarms   = sum(1 for e in event_log if e["type"] == "ALARM")
    warnings = sum(1 for e in event_log if e["type"] == "WARNING")
    print(f"  Аварий: {alarms}  |  Предупреждений: {warnings}")
    print("=" * 65)


# ---------------------------------------------------------------------------
# Вывод итогового журнала
# ---------------------------------------------------------------------------
def print_event_log() -> None:
    print("\n" + "=" * 65)
    print("  ЖУРНАЛ СОБЫТИЙ")
    print("=" * 65)
    for entry in event_log:
        print(f"  [{entry['type']:7s}] {entry['time']}  "
              f"Секция {entry['section']}: {entry['message']}")
    print("=" * 65)


# ---------------------------------------------------------------------------
# Точка входа
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # poll_interval=0 — быстрый запуск для демонстрации
    run_scada(cycles=10, poll_interval=0)
    print_event_log()
