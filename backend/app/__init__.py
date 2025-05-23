from flask import Flask
from flask_mongoengine import MongoEngine
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from flask_cors import CORS
import redis
from config import Config # 导入配置

# 初始化扩展
db = MongoEngine()
api_restful = Api() # Flask-Restful Api 对象
jwt = JWTManager()
# 初始化 SocketIO，使用线程模式，允许所有源
socketio = SocketIO(cors_allowed_origins="*", async_mode='threading', logger=True, engineio_logger=True)
redis_client = None # Redis 客户端将在 create_app 中初始化

def create_app(config_class=Config):
    """应用工厂函数"""
    app = Flask(__name__)
    app.config.from_object(config_class) # 从配置对象加载配置

    # 启用 CORS
    CORS(app, resources={r"/*": {"origins": "*"}})

    # 初始化 Flask 扩展
    db.init_app(app)
    jwt.init_app(app)
    
    # 初始化 SocketIO，但不使用 Redis（不需要消息队列）
    socketio.init_app(app, cors_allowed_origins="*")
    
    # 初始化 Redis 客户端 (仍然保留 Redis 连接，用于其他功能，但不用于 SocketIO)
    global redis_client
    redis_client = redis.from_url(app.config['REDIS_URL'])
    try:
        redis_client.ping() # 测试 Redis 连接
        print("Successfully connected to Redis!")
    except redis.exceptions.ConnectionError as e:
        print(f"Could not connect to Redis: {e}")
        # 根据实际需求处理连接失败的情况，例如记录日志或退出应用

    # 注册蓝图和路由
    # 需要在这里导入并注册你的蓝图（例如用户、商品、聊天等模块）
    from .routes.user_routes import user_bp # 导入用户蓝图
    app.register_blueprint(user_bp, url_prefix='/api/users') # 注册用户蓝图，并设置 URL 前缀
    
    # 注册认证路由，使用相同的蓝图但是不同的URL前缀和名称
    app.register_blueprint(user_bp, url_prefix='/api/auth', name='auth_bp')

    # 导入并注册商品蓝图
    from .routes.item_routes import item_bp
    app.register_blueprint(item_bp, url_prefix='/api/items')

    # 导入并注册消息蓝图
    from .routes.message_routes import message_bp
    app.register_blueprint(message_bp, url_prefix='/api/messages')

    # 导入并注册数据分析蓝图
    from .routes.analytics_routes import analytics_bp
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')

    # 导入并注册管理员蓝图
    from .routes.admin_routes import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    # 导入并注册评论蓝图
    from .routes.comment_routes import comment_bp
    app.register_blueprint(comment_bp, url_prefix='/api')

    # 注册 SocketIO 事件处理器
    from . import socket_handlers # 导入 SocketIO 事件处理函数
    socket_handlers.register_handlers(socketio)

    print(f"Flask App is running in {'DEBUG' if app.debug else 'PRODUCTION'} mode.")
    print(f"MongoDB URI: {app.config['MONGODB_SETTINGS']['host']}")
    print(f"Redis URL: {app.config['REDIS_URL']}")
    print(f"SocketIO async mode: {socketio.async_mode}")

    return app 