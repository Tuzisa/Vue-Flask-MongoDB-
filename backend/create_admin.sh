#!/bin/bash
echo "正在安装所需依赖..."
pip install -r requirements_admin.txt

echo ""
echo "正在创建管理员用户..."
python create_admin.py
echo ""
echo "如果要创建自定义管理员，请使用："
echo "python create_admin.py 用户名 邮箱 密码"
echo ""
read -p "按回车键继续..." 