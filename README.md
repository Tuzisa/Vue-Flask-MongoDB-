 # 二手交易平台（我的期末作业，基本功能都有，如果有需要可以拉走）

Two手交易平台是一个现代化的二手物品交易网站，为用户提供便捷的二手物品买卖服务。

## 项目架构

### 前端 (Frontend)
- 框架：Vue 3
- UI组件库：Element Plus
- 状态管理：Pinia
- 路由：Vue Router
- HTTP客户端：Axios

### 后端 (Backend)
- 框架：Flask (Python)
- 数据库：MongoDB
- 认证：JWT (JSON Web Tokens)
- 文件存储：本地文件系统

## 功能特点

- 用户认证与授权
- 商品发布与管理
- 商品分类浏览
- 评论系统
- 收藏功能
- 用户消息系统
- 管理员后台

## 项目结构

```
project/
├── frontend/                # 前端项目目录
│   ├── src/
│   │   ├── assets/         # 静态资源
│   │   ├── components/     # 通用组件
│   │   ├── pages/         # 页面组件
│   │   ├── stores/        # Pinia状态管理
│   │   ├── router/        # 路由配置
│   │   └── App.vue        # 根组件
│   └── package.json
│
├── backend/                # 后端项目目录
│   ├── app/
│   │   ├── models/        # 数据模型
│   │   ├── routes/        # API路由
│   │   ├── utils/         # 工具函数
│   │   └── __init__.py    # Flask应用初始化
│   └── requirements.txt    # Python依赖
```

## 安装与运行

### 前端部署

1. 安装依赖
```bash
cd frontend
npm install
```

2. 开发环境运行
```bash
npm run dev
```

3. 生产环境构建
```bash
npm run build
```

### 后端部署

1. 创建虚拟环境（推荐）
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. 安装依赖
```bash
cd backend
pip install -r requirements.txt
```

3. 启动服务器
```bash
python main.py
```

### 创建管理员账户

在后端目录下创建 `create_admin.py` 文件：

```python
from app import create_app
from app.models.user_model import User
from app.extensions import db

def create_admin_user():
    app = create_app()
    with app.app_context():
        # 检查管理员是否已存在
        admin = User.objects(username='admin').first()
        if admin:
            print("管理员账户已存在")
            return
        
        # 创建管理员用户
        admin = User(
            username='admin',
            email='admin@example.com',
            password_hash='admin123',  # demo版本使用明文密码
            plain_password='admin123', # 用于明文密码验证
            is_admin=True
        )
        admin.save()
        print("管理员账户创建成功")

if __name__ == '__main__':
    create_admin_user()
```

运行脚本创建管理员账户：
```bash
cd backend
python create_admin.py
```

默认管理员账户：
- 用户名：admin
- 密码：admin123

**注意：** 创建后请立即修改默认密码！


## 环境要求

- Node.js >= 16.0.0
- Python >= 3.8
- MongoDB >= 4.4
- npm >= 8.0.0

## 配置说明

### 前端配置
在 `.env` 文件中配置：
```
VITE_API_BASE_URL=http://localhost:3000/api
```

### 后端配置
在 `config.py` 文件中配置：
```python
MONGODB_SETTINGS = {
    'host': 'mongodb://localhost:27017/two_hand_platform'
}
SECRET_KEY = 'your-secret-key'
```

## API文档

主要API端点：

- 用户认证
  - POST /api/auth/register - 用户注册
  - POST /api/auth/login - 用户登录
  - POST /api/auth/logout - 用户登出

- 商品管理
  - GET /api/items - 获取商品列表
  - POST /api/items - 发布新商品
  - GET /api/items/:id - 获取商品详情
  - PUT /api/items/:id - 更新商品信息
  - DELETE /api/items/:id - 删除商品

- 评论管理
  - GET /api/comments - 获取评论列表
  - POST /api/comments - 发表评论
  - DELETE /api/comments/:id - 删除评论

## 开发团队

- 前端开发
- 后端开发
- UI/UX设计

## 许可证

本项目采用 MIT 许可证
