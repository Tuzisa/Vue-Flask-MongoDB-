@echo off
echo 正在安装所需依赖...
pip install pymongo werkzeug

echo.
echo 正在修复管理员用户...
python fix_admin.py
echo.
echo 修复完成，请重新启动服务器并尝试登录。
echo.
pause 