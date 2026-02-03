import time
import psutil
import os
import winreg
import re

INTERVAL = 60
CHECKS = 5

def get_steam_path():
    with winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Software\Valve\Steam"
    ) as key:
        path, _ = winreg.QueryValueEx(key, "SteamPath")
        return path


def get_active_app(steam_path):
    steamapps = os.path.join(steam_path, "steamapps")

    for fname in os.listdir(steamapps):
        if fname.startswith("appmanifest") and fname.endswith(".acf"):
            path = os.path.join(steamapps, fname)
            with open(path, encoding="utf-8", errors="ignore") as f:
                data = f.read()
            if '"StateFlags"\t\t"4"' in data or '"StateFlags"\t\t"1026"' in data:
                name = re.search(r'"name"\s+"(.+?)"', data)
                return name.group(1) if name else "Неизвестная игра"
    return None

def steam_is_running():
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and 'steam' in proc.info['name'].lower():
            return True
    return False

def main():
    steam_path = get_steam_path()
    print(f"Steam находится по адресу: {steam_path}\n")

    prev_bytes = psutil.net_io_counters().bytes_recv
    for i in range(1, CHECKS + 1):
        time.sleep(INTERVAL)
        current_bytes = psutil.net_io_counters().bytes_recv
        delta = current_bytes - prev_bytes
        speed_mb = delta / INTERVAL / (1024 * 1024)
        game = get_active_app(steam_path)
        steam_running = steam_is_running()

        if game and steam_running and speed_mb > 0.1:
            status = "downloading"
        elif game:
            status = "paused"
            speed_mb = 0.0
        else:
            status = "idle"
            speed_mb = 0.0
            game = "Нет активной загрузки"

        print(f"Времени прошло: {i}/5 минут")
        print(f"Игра: {game}")
        print(f"Статус: {status}")
        print(f"Скорость загрузки: {speed_mb:.2f} MB/s\n")
        prev_bytes = current_bytes

if __name__ == "__main__":
    main()