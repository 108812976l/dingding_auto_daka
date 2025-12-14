import os
import re
import subprocess
import time

ADB = r"C:\adb\platform-tools\adb.exe"

# -------------------- 基础功能 -------------------- #

def get_current_activity():
    """获取当前前台 Activity"""
    result = subprocess.run(
        [ADB, "shell", "dumpsys", "activity", "activities"],
        capture_output=True, text=True
    )
    for line in result.stdout.splitlines():
        if "mResumedActivity" in line or "mFocusedActivity" in line:
            parts = line.split()
            for part in parts:
                if '/' in part:
                    return part.split('}')[0]
    return None

def bring_dingding_foreground():
    """把钉钉拉回前台"""
    os.system(f'"{ADB}" shell am start -n com.alibaba.android.rimet/.biz.LaunchHomeActivity')
    time.sleep(1)

def ensure_dingding_ready():
    """确保钉钉在前台"""
    current = get_current_activity()
    if current is None or "com.alibaba.android.rimet" not in current:
        bring_dingding_foreground()
    time.sleep(1)

def get_bounds_by_text(text, timeout=2):
    """通过 text 获取控件坐标"""
    for _ in range(timeout*2):
        xml = os.popen(f'"{ADB}" shell uiautomator dump /dev/tty').read()
        match = re.search(rf'text="{text}".*?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml)
        if match:
            x1, y1, x2, y2 = map(int, match.groups())
            x = (x1 + x2) // 2
            y = (y1 + y2) // 2
            return x, y
        time.sleep(0.5)
    return None, None

def click_text_with_retry(text, max_wait=20):
    """循环点击 text，直到成功或超时"""
    start_time = time.time()
    while time.time() - start_time < max_wait:
        ensure_dingding_ready()  # 保证钉钉在前台
        x, y = get_bounds_by_text(text, timeout=1)
        if x and y:
            os.system(f'"{ADB}" shell input tap {x} {y}')
            print(f"已点击 {text} @ ({x},{y})")
            time.sleep(1)
            # 再次检查控件是否消失，确认点击生效
            x2, y2 = get_bounds_by_text(text, timeout=1)
            if x2 is None:
                return True
        else:
            # 没找到控件，尝试上下滑动屏幕
            os.system(f'"{ADB}" shell input swipe 500 1500 500 500 300')
        time.sleep(0.5)
    print(f"点击 {text} 超时失败")
    return False

def wait(seconds, desc="等待中"):
    for i in range(seconds, 0, -1):
        print(f"{desc}: {i}s")
        time.sleep(1)

# -------------------- 主流程 -------------------- #

if __name__ == "__main__":
    print("启动钉钉...")
    os.system(f'"{ADB}" shell input keyevent 224')  # 点亮屏幕
    os.system(f'"{ADB}" shell input swipe 540 2000 540 800 300')  # 解锁
    os.system(f'"{ADB}" shell am start -n com.alibaba.android.rimet/.biz.LaunchHomeActivity')
    wait(3, "等待钉钉启动完成")

    print("切换工作台...")
    if click_text_with_retry("工作台", max_wait=15):
        wait(2)
        print("点击打卡...")
        click_text_with_retry("打卡", max_wait=20)
    else:
        print("切换工作台失败，脚本结束")

    wait(3)
    print("打卡流程结束，关闭钉钉")
    os.system(f'"{ADB}" shell am force-stop com.alibaba.android.rimet')
