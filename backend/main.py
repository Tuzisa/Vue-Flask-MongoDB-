# 不使用 eventlet，避免 Python 3.13 兼容性问题
# 注意：这种模式在生产环境中性能较低，生产环境建议使用 Python 3.10/3.11 + eventlet

from app import create_app, socketio # 从 app 包导入 create_app 函数和 socketio 实例

app = create_app() # 创建 Flask 应用实例

if __name__ == '__main__':
    # 使用 SocketIO 的 run 方法来启动服务器
    print("Starting Flask application with Socket.IO (threading mode)...")
    print("Note: This mode has lower performance. For production, use Python 3.10/3.11 with eventlet")
    socketio.run(app, 
                host='0.0.0.0', 
                port=5000, 
                debug=app.config['DEBUG'], 
                use_reloader=app.config['DEBUG'],
                allow_unsafe_werkzeug=True if app.config['DEBUG'] else False
                ) 