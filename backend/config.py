import os
from dotenv import load_dotenv

load_dotenv() # 加载 .env 文件中的环境变量

class Config:
    """基础配置类"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key' # 应用密钥，用于 session 加密等
    MONGODB_SETTINGS = {
        'db': os.environ.get('MONGO_DB_NAME') or 'community_marketplace', # MongoDB 数据库名称
        'host': os.environ.get('MONGO_URI') or 'mongodb://localhost:27017/community_marketplace' # MongoDB 连接 URI
    }
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'your-jwt-secret-key' # JWT 密钥
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0' # Redis 连接 URL
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true' # 是否开启 Debug 模式
    # 可以根据需要添加更多配置项
    # 例如：
    # UPLOAD_FOLDER = 'uploads'
    # MAX_CONTENT_LENGTH = 16 * 1024 * 1024 # 16MB 