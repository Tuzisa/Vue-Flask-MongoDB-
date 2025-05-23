#!/usr/bin/env python
import os
import sys
from pymongo import MongoClient
from config import Config

def check_admin_users():
    """检查数据库中的管理员用户"""
    # 从配置中获取MongoDB连接信息
    mongo_settings = Config.MONGODB_SETTINGS
    mongo_uri = mongo_settings.get('host', 'mongodb://localhost:27017/nosql_project')
    
    print(f"连接到数据库: {mongo_uri}")
    
    # 连接MongoDB
    client = MongoClient(mongo_uri)
    
    # 获取数据库名
    db_name = mongo_uri.split('/')[-1]
    db = client[db_name]
    
    # 获取users集合
    users_collection = db['users']
    
    # 查找所有用户
    all_users = list(users_collection.find())
    print(f"数据库中共有 {len(all_users)} 个用户")
    
    # 查找管理员用户
    admin_users = list(users_collection.find({'is_admin': True}))
    print(f"其中有 {len(admin_users)} 个管理员用户")
    
    # 打印管理员用户信息
    if admin_users:
        print("\n管理员用户列表:")
        for user in admin_users:
            print(f"ID: {user.get('_id')}")
            print(f"用户名: {user.get('username')}")
            print(f"邮箱: {user.get('email')}")
            print(f"是否管理员: {user.get('is_admin')}")
            print("-" * 30)
    else:
        print("\n没有找到管理员用户!")
    
    # 查找特定的管理员用户
    admin = users_collection.find_one({'email': 'admin@example.com'})
    if admin:
        print("\n默认管理员用户信息:")
        print(f"ID: {admin.get('_id')}")
        print(f"用户名: {admin.get('username')}")
        print(f"邮箱: {admin.get('email')}")
        print(f"是否管理员: {admin.get('is_admin')}")
        print(f"密码哈希: {admin.get('password_hash')[:20]}...")
    else:
        print("\n没有找到默认管理员用户!")

if __name__ == '__main__':
    check_admin_users() 