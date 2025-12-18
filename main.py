import os
import re
import time
import json
import traceback
import urllib.request
from datetime import datetime

ADB = r"C:\adb\platform-tools\adb.exe"
LOG_FILE = "logs.txt"


# ---------- 拉取节假日列表 ----------
def get_holidays(year: int) -> dict:
    filename = f"{year}_holidays.json"

    if not os.path.exists(filename):
        url = f"https://fastly.jsdelivr.net/gh/NateScarlet/holiday-cn@master/{year}.json"
        with urllib.request.urlopen(url) as response:
            data = response.read()
        with open(filename, "wb") as f:
            f.write(data)

    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)


def build_holidays_map(holiday_json: dict) -> dict:
    return {
        day["date"]: {
            "isOffDay": day["isOffDay"],
            "name": day["name"]
        }
        for day in holiday_json.get("days", [])
    }


def is_workday(today: datetime, day_map: dict) -> tuple[bool, str]:
    date_str = today.strftime("%Y-%m-%d")

    if date_str in day_map:
        info = day_map[date_str]
        return (not info["isOffDay"]), info["name"]

    return (today.weekday() < 5, "普通工作日")


def log_error(step: str, e: Exception):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{now} --->  [error] {step}:{e}\n")
        f.write(traceback.format_exc())
        f.write("\n")
    print(f"[error] {step}:{e}]")


def log(message: str):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{now} ---> {message}\n")
    print(message)


# ---------- 滑动解锁 ----------
def unlock_screen():
    try:
        os.system(f'"{ADB}" shell input keyevent 224')
        time.sleep(1)
        os.system(f'"{ADB}" shell input swipe 540 2000 540 800 300')
        time.sleep(1)
    except Exception as e:
        log_error("解锁屏幕失败", e)
        raise


# ---------- 打开钉钉 ----------
def open_dingding():
    try:
        os.system(f'"{ADB}" shell am start -n com.alibaba.android.rimet/.biz.LaunchHomeActivity')
        time.sleep(3)
    except Exception as e:
        log_error("打开钉钉失败",e)
        raise


# ---------- 杀死钉钉 ----------
def kill_dingding():
    try:
        os.system(f'"{ADB}" shell am force-stop com.alibaba.android.rimet')
        time.sleep(1)
    except Exception as e:
        log_error("结束钉钉程序失败",e)
        raise


# ---------- 点击打卡 ----------
def click_daka():
    xml = os.popen(f'"{ADB}" shell uiautomator dump /dev/tty').read()
    match = re.search(r'text="打卡".*?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml)
    if match:
        x1, y1, x2, y2 = map(int, match.groups())
        x = (x1 + x2) // 2
        y = (y1 + y2) // 2
        os.system(f'"{ADB}" shell input tap {x} {y}')
        time.sleep(1)
        return True
    return False


# ---------- 主流程 ----------
if __name__ == "__main__":
    try:
        today = datetime.now()
        year = today.year

        holiday_json = get_holidays(year)
        day_map = build_holidays_map(holiday_json)

        workday, reason = is_workday(today, day_map)

        if not workday:
            log(f"{reason},跳过")
            exit(0)

        if workday:
            kill_dingding()
            unlock_screen()
            open_dingding()
            time.sleep(3)
            log("工作日打卡")
            kill_dingding()
    except Exception as e:
        log_error("主流程异常",e)
        log("脚本异常结束")
