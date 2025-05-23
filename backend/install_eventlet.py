import subprocess
import sys
import os

def install_packages():
    """安装必要的依赖包"""
    packages = [
        'eventlet==0.33.3',  # 使用稳定版本的 eventlet
        'flask-socketio>=5.3.0',
        'python-socketio>=5.7.0',
    ]
    
    print("Installing required packages...")
    for package in packages:
        print(f"Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"Successfully installed {package}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to install {package}: {e}")
            return False
    
    print("All packages successfully installed!")
    return True

if __name__ == "__main__":
    if install_packages():
        print("\n依赖安装完成，请重新运行 python main.py 启动服务器")
    else:
        print("\n依赖安装失败，请手动运行以下命令安装：")
        print("pip install eventlet==0.33.3 flask-socketio>=5.3.0 python-socketio>=5.7.0") 