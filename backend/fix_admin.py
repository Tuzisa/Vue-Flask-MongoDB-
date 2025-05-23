#!/usr/bin/env python
import os
import sys
from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from config import Config
from datetime import datetime

def fix_admin_user():
    """修复管理员用户"""
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
    
    # 查找admin用户
    admin = users_collection.find_one({'email': 'admin@example.com'})
    
    if admin:
        print(f"找到admin用户: {admin.get('username')}")
        
        # 确保is_admin字段为True
        if not admin.get('is_admin'):
            users_collection.update_one(
                {'_id': admin['_id']},
                {'$set': {'is_admin': True}}
            )
            print("已将用户设置为管理员")
        else:
            print("用户已经是管理员")
        
        # 重置密码
        users_collection.update_one(
            {'_id': admin['_id']},
            {'$set': {'password_hash': generate_password_hash('admin123')}}
        )
        print("已重置密码为: admin123")
        
        # 打印更新后的用户信息
        admin = users_collection.find_one({'email': 'admin@example.com'})
        print("\n更新后的管理员信息:")
        print(f"ID: {admin.get('_id')}")
        print(f"用户名: {admin.get('username')}")
        print(f"邮箱: {admin.get('email')}")
        print(f"是否管理员: {admin.get('is_admin')}")
        print(f"密码哈希: {admin.get('password_hash')[:20]}...")
    else:
        print("未找到admin用户，创建新用户...")
        
        # 创建新的admin用户
        new_admin = {
            'username': 'admin',
            'email': 'admin@example.com',
            'password_hash': generate_password_hash('admin123'),
            'is_admin': True,
            'created_at': datetime.now(),
            'browse_history': [],
            'favorites': [],
            'avatar_url': None,
            'bio': '系统管理员'
        }
        
        # 插入新用户
        result = users_collection.insert_one(new_admin)
        
        print(f"已创建新的管理员用户，ID: {result.inserted_id}")
        print("用户名: admin")
        print("邮箱: admin@example.com")
        print("密码: admin123")

if __name__ == '__main__':
    fix_admin_user()