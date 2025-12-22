@echo off
chcp 65001
@echo off
REM -------------------------------
REM 自动打卡启动脚本
REM -------------------------------

REM 设置Python路径
set PYTHON_EXE=C:\Users\Administrator\AppData\Local\Programs\Python\Python312\python.exe

REM 设置脚本路径
set SCRIPT_PATH=C:\tools\dingding_auto_daka\dingding_auto_daka\main.py

REM 进入脚本目录
cd /d %~dp0

REM 执行Python脚本
"%PYTHON_EXE%" "%SCRIPT_PATH%"

REM 完成提示
echo 打卡脚本已执行完成

exit
