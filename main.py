import os
import re
import subprocess
import time
from datetime import datetime

ADB = r"C:\adb\platform-tools\adb.exe"
LOG_FILE = "logs.txt"

# ---------- 节假日列表 ----------
HOLIDAYS_2025 = [
    "2025-01-01",
    "2025-01-31","2025-02-01","2025-02-02","2025-02-03","2025-02-04","2025-02-05","2025-02-06",  # 春节
    "2025-04-05",  # 清明
    "2025-05-01","2025-05-02","2025-05-03",  # 劳动节
    "2025-06-22","2025-06-23","2025-06-24",  # 端午
    "2025-09-10","2025-09-11","2025-09-12",  # 中秋
    "2025-10-01","2025-10-02","2025-10-03","2025-10-04","2025-10-05","2025-10-06","2025-10-07"  # 国庆
]

def is_workday(date_str: str) -> bool:
    """判断今天是否上班"""
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    weekday = date_obj.weekday()  # 周一=0，周日=6
    if weekday >= 5:  # 周末
        return False
    if date_str in HOLIDAYS_2025:
        return False
    return True

def log(message: str):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{now} ---> {message}\n")
    print(message)

# ---------- 滑动解锁 ----------
def unlock_screen():
    os.system(f'"{ADB}" shell input keyevent 224')  # 点亮屏幕
    time.sleep(1)
    os.system(f'"{ADB}" shell input swipe 540 2000 540 800 300')  # 解锁
    time.sleep(1)

# ---------- 打开钉钉 ----------
def open_dingding():
    os.system(f'"{ADB}" shell am start -n com.alibaba.android.rimet/.biz.LaunchHomeActivity')
    time.sleep(3)

# ---------- 杀死钉钉 ----------
def kill_dingding():
    os.system(f'"{ADB}" shell am force-stop com.alibaba.android.rimet')
    time.sleep(1)

# ---------- 点击打卡 ----------
def click_daka():
    # 用简单点击方式，假设钉钉已在前台
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
    today = datetime.now().strftime("%Y-%m-%d")
    if is_workday(today):
        unlock_screen()
        open_dingding()
        if click_daka():
            log("打卡成功")
        else:
            log("打卡失败")
        kill_dingding()
    else:
        log("放假，跳过")
