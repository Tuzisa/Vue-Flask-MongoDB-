#!/usr/bin/env python
import os
import sys
from flask import Flask
from werkzeug.security import generate_password_hash
from pymongo import MongoClient
from datetime import datetime
from config import Config

def create_admin_user(username='admin', email='admin@example.com', password='admin123'):
    """创建管理员用户"""
    # 从配置中获取MongoDB连接信息
    mongo_settings = Config.MONGODB_SETTINGS
    mongo_uri = mongo_settings.get('host', 'mongodb://localhost:27017/nosql_project')
    
    # 连接MongoDB
    client = MongoClient(mongo_uri)
    
    # 获取数据库名
    db_name = mongo_uri.split('/')[-1]
    db = client[db_name]
    
    # 获取users集合
    users_collection = db['users']
    
    # 检查用户是否已存在
    existing_user = users_collection.find_one({'email': email})
    
    if existing_user:
        print(f"用户 {email} 已存在!")
        
        # 如果用户存在但不是管理员，则更新为管理员
        if not existing_user.get('is_admin', False):
            users_collection.update_one(
                {'_id': existing_user['_id']},
                {'$set': {'is_admin': True}}
            )
            print(f"已将用户 {email} 设置为管理员")
        
        # 如果需要重置密码
        if len(sys.argv) > 1 and sys.argv[1] == '--reset-password':
            users_collection.update_one(
                {'_id': existing_user['_id']},
                {'$set': {'password_hash': generate_password_hash(password)}}
            )
            print(f"已重置用户 {email} 的密码")
    else:
        # 创建新管理员用户
        new_user = {
            'username': username,
            'email': email,
            'password_hash': generate_password_hash(password),
            'is_admin': True,
            'created_at': datetime.utcnow(),
            'browse_history': [],
            'favorites': [],
            'avatar_url': None,
            'bio': ''
        }
        
        # 插入新用户
        users_collection.insert_one(new_user)
        
        print(f"管理员用户创建成功!")
        print(f"用户名: {username}")
        print(f"邮箱: {email}")
        print(f"密码: {password}")

if __name__ == '__main__':
    # 可以通过命令行参数自定义管理员信息
    if len(sys.argv) > 3:
        create_admin_user(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        # 使用默认值
        create_admin_user() 