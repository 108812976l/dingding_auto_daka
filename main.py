import os
import re
import subprocess
import time
import datetime
import random
import holidays

def get_screen_size():
    #获取屏幕分辨率
    result = subprocess.check_output(
        ["adb","shell","wm","size"],
        encoding="utf-8",
    )

    match = re.search(r"Physical size:\s*(\d+)x(\d+)",result)
    if not match:
        raise RuntimeError("无法获取屏幕分辨率")

def worktime_is()->bool:
    #工作日判断
    today = datetime.date.today()
    print(today)
    cn_holidays = holidays.country_holidays("CN",years=today.year)
    if today in cn_holidays:
        return False

    if today.weekday() >= 5:
        return False

    return True

def daka_judge():
    if worktime_is:
        daka_main()
    else:
        print("yes")

def daka_main():
    os.system("adb shell input keyevent 26") #点亮屏幕
    os.system("adb shell input swipe 555 1600 500 500 500")
    os.system("adb shell monkey -p com.alibaba.android.rimet -c android.intent.category.LAUNCHER 1")
    time.sleep(10) #10s延迟
    os.system("adb shell input tap 555 1850")
    time.sleep(10)
    os.system("adb shell input tap 150 1010")



if __name__ == '__main__':
    daka_judge()
