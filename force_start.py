import time

from main import open_dingding, kill_dingding, log, unlock_screen

if __name__ == '__main__':
    kill_dingding()
    unlock_screen()
    open_dingding()
    time.sleep(5)
    log("打卡（手动强制启动）")
    kill_dingding()
