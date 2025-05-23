from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from ..models.user_model import User # 导入用户模型
from ..models.item_model import Item
from mongoengine.errors import NotUniqueError, ValidationError
import datetime
import pymongo
import os
import uuid
from werkzeug.utils import secure_filename

user_bp = Blueprint('user_bp', __name__) # 创建蓝图

# 设置允许的图片文件扩展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
# 设置上传文件夹
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'avatars')

# 确保上传文件夹存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@user_bp.route('/health', methods=['GET'])
def health_check():
    """服务健康检查端点"""
    try:
        # 检查MongoDB连接
        db_status = "connected"
        db_error = None
        
        try:
            # 尝试执行一个简单的查询来验证数据库连接
            User._get_collection().find_one({}, {"_id": 1})
        except pymongo.errors.ConnectionFailure as e:
            db_status = "disconnected"
            db_error = str(e)
        except Exception as e:
            db_status = "error"
            db_error = str(e)
        
        # 返回系统状态
        return jsonify({
            "status": "ok" if db_status == "connected" else "error",
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "database": {
                "status": db_status,
                "error": db_error
            },
            "service": {
                "name": "community-trading-platform-api",
                "version": "1.0.0"
            }
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "error": str(e)
        }), 500

@user_bp.route('/register', methods=['POST'])
def register():
    """用户注册接口"""
    data = request.get_json()
    if not data:
        return jsonify({"msg": "Missing JSON in request"}), 400

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({"msg": "Missing username, email, or password"}), 400

    try:
        # 检查用户名或邮箱是否已存在 (虽然模型定义了 unique，但这里可以提前检查并给出更友好的提示)
        if User.objects(username=username).first():
            return jsonify({"msg": "Username already exists"}), 409 # 409 Conflict
        if User.objects(email=email).first():
            return jsonify({"msg": "Email already registered"}), 409

        new_user = User(username=username, email=email)
        new_user.set_password(password) # 哈希密码
        new_user.save() # 保存到数据库
        return jsonify({"msg": "User registered successfully"}), 201 # 201 Created
    except NotUniqueError: # MongoEngine 会在 unique 字段冲突时抛出此异常
        return jsonify({"msg": "Username or email already exists"}), 409
    except ValidationError as e:
        return jsonify({"msg": "Validation error", "errors": e.to_dict()}), 400
    except Exception as e:
        # 记录更详细的服务器错误日志
        print(f"Error during registration: {e}")
        return jsonify({"msg": "An internal error occurred"}), 500

@user_bp.route('/login', methods=['POST'])
def login():
    """用户登录接口"""
    data = request.get_json()
    if not data:
        return jsonify({"msg": "Missing JSON in request"}), 400

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"msg": "Missing email or password"}), 400

    user = User.objects(email=email).first() # 通过邮箱查找用户

    if user and user.check_password(password):
        access_token = create_access_token(identity=str(user.id)) # 使用用户 ID 作为 JWT 的 identity
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"msg": "Invalid email or password"}), 401 # 401 Unauthorized

@user_bp.route('/refresh', methods=['POST'])
@jwt_required()
def refresh_token():
    """刷新用户访问令牌"""
    current_user_id = get_jwt_identity()
    
    try:
        # 验证用户是否存在
        user = User.objects(id=current_user_id).first()
        if not user:
            return jsonify({"msg": "User not found"}), 404
        
        # 创建新的访问令牌，可以添加过期时间等参数
        access_token = create_access_token(
            identity=current_user_id,
            expires_delta=datetime.timedelta(days=1)
        )
        
        return jsonify(access_token=access_token), 200
    except Exception as e:
        print(f"Error refreshing token: {e}")
        return jsonify({"msg": "Failed to refresh token"}), 500

@user_bp.route('/check', methods=['GET'])
@jwt_required()
def check_auth():
    """检查用户认证状态"""
    current_user_id = get_jwt_identity()
    
    try:
        user = User.objects(id=current_user_id).first()
        if not user:
            return jsonify({"authenticated": False, "msg": "User not found"}), 404
        
        return jsonify({
            "authenticated": True,
            "user_id": current_user_id,
            "username": user.username,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        print(f"Error checking authentication: {e}")
        return jsonify({"authenticated": False, "msg": "Authentication check failed"}), 500

@user_bp.route('/browse-history', methods=['GET'])
@jwt_required()
def get_browse_history():
    """获取用户浏览历史"""
    current_user_id = get_jwt_identity()
    
    try:
        user = User.objects(id=current_user_id).first()
        if not user:
            return jsonify({"msg": "User not found"}), 404

        # 假设user.browse_history是一个列表，包含 {item_id, viewed_at} 的字典
        history = []
        
        if hasattr(user, 'browse_history'):
            for entry in user.browse_history:
                try:
                    item = Item.objects(id=entry['item_id']).first()
                    if item:  # 确保商品仍然存在
                        history.append({
                            "id": str(item.id),
                            "title": item.title,
                            "price": item.price,
                            "images": item.images,
                            "category": item.category,
                            "viewedAt": entry['viewed_at'].isoformat()
                        })
                except Exception as e:
                    print(f"Error getting history item: {e}")
        
        return jsonify({"history": history}), 200
    
    except Exception as e:
        print(f"Error getting browse history: {e}")
        return jsonify({"msg": "An internal error occurred"}), 500

@user_bp.route('/browse-history/<item_id>', methods=['POST'])
@jwt_required()
def add_to_browse_history(item_id):
    """添加商品到浏览历史"""
    current_user_id = get_jwt_identity()
    
    try:
        user = User.objects(id=current_user_id).first()
        if not user:
            return jsonify({"msg": "User not found"}), 404
        
        # 检查商品是否存在
        item = Item.objects(id=item_id).first()
        if not item:
            return jsonify({"msg": "Item not found"}), 404
        
        # 准备历史记录条目
        history_entry = {
            "item_id": item_id,
            "viewed_at": datetime.datetime.utcnow()
        }
        
        # 检查是否已经有browse_history字段
        if not hasattr(user, 'browse_history'):
            user.browse_history = []
        
        # 检查是否已在历史记录中，如果是则删除旧记录
        for i, entry in enumerate(user.browse_history):
            if entry['item_id'] == item_id:
                user.browse_history.pop(i)
                break
        
        # 添加到历史记录的开头
        user.browse_history.insert(0, history_entry)
        
        # 仅保留最近的30条记录
        if len(user.browse_history) > 30:
            user.browse_history = user.browse_history[:30]
        
        user.save()
        
        return jsonify({"msg": "Item added to browse history"}), 200
    
    except Exception as e:
        print(f"Error adding to browse history: {e}")
        return jsonify({"msg": "An internal error occurred"}), 500

@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """获取用户个人资料"""
    current_user_id = get_jwt_identity()
    
    try:
        user = User.objects(id=current_user_id).first()
        if not user:
            return jsonify({"msg": "User not found"}), 404
            
        # 返回用户信息，不包含敏感数据
        return jsonify({
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at.isoformat() if hasattr(user, 'created_at') else None,
            "avatar": user.avatar_url if hasattr(user, 'avatar_url') else None,
            "bio": user.bio if hasattr(user, 'bio') else None
        }), 200
    except Exception as e:
        print(f"Error getting user profile: {e}")
        return jsonify({"msg": "An internal error occurred"}), 500

@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """更新用户个人资料"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data:
        return jsonify({"msg": "Missing JSON in request"}), 400
        
    try:
        user = User.objects(id=current_user_id).first()
        if not user:
            return jsonify({"msg": "User not found"}), 404
            
        # 更新可以修改的字段
        if 'username' in data and data['username'] != user.username:
            # 检查新用户名是否已存在
            if User.objects(username=data['username']).first():
                return jsonify({"msg": "Username already exists"}), 409
            user.username = data['username']
            
        if 'bio' in data:
            user.bio = data['bio']
            
        if 'avatar_url' in data:
            user.avatar_url = data['avatar_url']
            
        # 保存更改
        user.save()
        
        return jsonify({
            "msg": "Profile updated successfully",
            "user": {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "bio": user.bio if hasattr(user, 'bio') else None,
                "avatar": user.avatar_url if hasattr(user, 'avatar_url') else None
            }
        }), 200
    except Exception as e:
        print(f"Error updating user profile: {e}")
        return jsonify({"msg": "An internal error occurred"}), 500

@user_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """获取当前登录用户的信息"""
    current_user_id = get_jwt_identity()
    
    try:
        user = User.objects(id=current_user_id).first()
        if not user:
            return jsonify({"msg": "User not found"}), 404
            
        # 返回用户信息，不包含敏感数据
        return jsonify({
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at.isoformat() if hasattr(user, 'created_at') else None,
            "avatar": user.avatar_url if hasattr(user, 'avatar_url') else None,
            "bio": user.bio if hasattr(user, 'bio') else None
        }), 200
    except Exception as e:
        print(f"Error getting user info: {e}")
        return jsonify({"msg": "An internal error occurred"}), 500

@user_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_user():
    """更新当前用户信息"""
    current_user_id = get_jwt_identity()
    
    try:
        user = User.objects(id=current_user_id).first()
        if not user:
            return jsonify({"msg": "User not found"}), 404
        
        # 检查内容类型
        content_type = request.headers.get('Content-Type', '')
        
        # 处理JSON请求
        if 'application/json' in content_type:
            data = request.get_json()
            if not data:
                return jsonify({"msg": "Missing JSON in request"}), 400
                
            # 更新可以修改的字段
            if 'username' in data and data['username'] != user.username:
                # 检查新用户名是否已存在
                if User.objects(username=data['username']).first():
                    return jsonify({"msg": "Username already exists"}), 409
                user.username = data['username']
                
            if 'bio' in data:
                user.bio = data['bio']
                
            if 'avatar_url' in data:
                user.avatar_url = data['avatar_url']
            
            # 保存更改
            user.save()
            
            return jsonify({
                "msg": "User information updated successfully",
                "user": {
                    "id": str(user.id),
                    "username": user.username,
                    "email": user.email,
                    "bio": user.bio if hasattr(user, 'bio') else None,
                    "avatar": user.avatar_url if hasattr(user, 'avatar_url') else None
                }
            }), 200
        
        # 处理multipart/form-data请求（用于文件上传）
        elif 'multipart/form-data' in content_type:
            # 更新基本信息
            if 'username' in request.form:
                new_username = request.form.get('username')
                if new_username != user.username:
                    # 检查新用户名是否已存在
                    if User.objects(username=new_username).first():
                        return jsonify({"msg": "Username already exists"}), 409
                    user.username = new_username
            
            if 'bio' in request.form:
                user.bio = request.form.get('bio')
            
            # 处理头像上传
            if 'avatar' in request.files:
                file = request.files['avatar']
                if file and allowed_file(file.filename):
                    # 生成安全的文件名
                    filename = secure_filename(file.filename)
                    # 添加UUID前缀避免文件名冲突
                    unique_filename = f"{uuid.uuid4()}_{filename}"
                    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
                    
                    # 保存文件
                    file.save(file_path)
                    
                    # 存储相对路径
                    relative_path = f"/static/avatars/{unique_filename}"
                    user.avatar_url = relative_path
            
            # 保存更改
            user.save()
            
            return jsonify({
                "msg": "User information updated successfully",
                "user": {
                    "id": str(user.id),
                    "username": user.username,
                    "email": user.email,
                    "bio": user.bio if hasattr(user, 'bio') else None,
                    "avatar": user.avatar_url if hasattr(user, 'avatar_url') else None
                }
            }), 200
        
        else:
            return jsonify({"msg": "Unsupported media type"}), 415
        
    except Exception as e:
        print(f"Error updating user: {e}")
        return jsonify({"msg": "An internal error occurred"}), 500

@user_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """修改用户密码"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data:
        return jsonify({"msg": "Missing JSON in request"}), 400
        
    if 'current_password' not in data or 'new_password' not in data:
        return jsonify({"msg": "Missing current or new password"}), 400
        
    try:
        user = User.objects(id=current_user_id).first()
        if not user:
            return jsonify({"msg": "User not found"}), 404
            
        # 验证当前密码
        if not user.check_password(data['current_password']):
            return jsonify({"msg": "Current password is incorrect"}), 401
            
        # 设置新密码
        user.set_password(data['new_password'])
        user.save()
        
        return jsonify({"msg": "Password changed successfully"}), 200
    except Exception as e:
        print(f"Error changing password: {e}")
        return jsonify({"msg": "An internal error occurred"}), 500

@user_bp.route('/favorites', methods=['GET'])
@jwt_required()
def get_favorites():
    """获取用户收藏的商品列表"""
    current_user_id = get_jwt_identity()
    
    try:
        user = User.objects(id=current_user_id).first()
        if not user:
            return jsonify({"msg": "User not found"}), 404
            
        # 初始化收藏列表
        favorites = []
        
        # 如果用户模型中有收藏字段
        if hasattr(user, 'favorites') and user.favorites:
            favorites = user.favorites
        else:
            # 如果用户模型中没有收藏字段，初始化一个空列表
            user.favorites = []
            user.save()
        
        return jsonify({"favorites": favorites}), 200
    except Exception as e:
        print(f"Error getting favorites: {e}")
        return jsonify({"msg": "An internal error occurred"}), 500

@user_bp.route('/favorites/<item_id>', methods=['POST'])
@jwt_required()
def add_favorite(item_id):
    """添加商品到收藏列表"""
    current_user_id = get_jwt_identity()
    
    try:
        user = User.objects(id=current_user_id).first()
        if not user:
            return jsonify({"msg": "User not found"}), 404
            
        # 检查商品是否存在
        item = Item.objects(id=item_id).first()
        if not item:
            return jsonify({"msg": "Item not found"}), 404
            
        # 初始化收藏列表（如果不存在）
        if not hasattr(user, 'favorites'):
            user.favorites = []
            
        # 检查是否已经收藏
        for fav in user.favorites:
            if fav.get('item_id') == item_id:
                return jsonify({"msg": "Item already in favorites", "success": True}), 200
                
        # 添加到收藏列表
        favorite_item = {
            "item_id": item_id,
            "added_at": datetime.datetime.utcnow()
        }
        user.favorites.append(favorite_item)
        user.save()
        
        return jsonify({
            "msg": "Item added to favorites",
            "success": True,
            "favorite": favorite_item
        }), 201
    except Exception as e:
        print(f"Error adding to favorites: {e}")
        return jsonify({"msg": "An internal error occurred", "success": False}), 500

@user_bp.route('/favorites/<item_id>', methods=['DELETE'])
@jwt_required()
def remove_favorite(item_id):
    """从收藏列表中移除商品"""
    current_user_id = get_jwt_identity()
    
    try:
        user = User.objects(id=current_user_id).first()
        if not user:
            return jsonify({"msg": "User not found"}), 404
            
        # 检查是否有收藏列表
        if not hasattr(user, 'favorites') or not user.favorites:
            return jsonify({"msg": "No favorites found", "success": True}), 200
            
        # 查找并移除收藏
        found = False
        for i, fav in enumerate(user.favorites):
            if fav.get('item_id') == item_id:
                user.favorites.pop(i)
                found = True
                break
                
        if found:
            user.save()
            return jsonify({"msg": "Item removed from favorites", "success": True}), 200
        else:
            return jsonify({"msg": "Item not found in favorites", "success": True}), 200
    except Exception as e:
        print(f"Error removing from favorites: {e}")
        return jsonify({"msg": "An internal error occurred", "success": False}), 500

@user_bp.route('/favorites/<item_id>/check', methods=['GET'])
@jwt_required()
def check_favorite(item_id):
    """检查商品是否已收藏"""
    current_user_id = get_jwt_identity()
    
    try:
        user = User.objects(id=current_user_id).first()
        if not user:
            return jsonify({"msg": "User not found"}), 404
            
        # 检查是否有收藏列表
        if not hasattr(user, 'favorites') or not user.favorites:
            return jsonify({"is_favorite": False}), 200
            
        # 检查是否已收藏
        for fav in user.favorites:
            if fav.get('item_id') == item_id:
                return jsonify({"is_favorite": True}), 200
                
        return jsonify({"is_favorite": False}), 200
    except Exception as e:
        print(f"Error checking favorite: {e}")
        return jsonify({"msg": "An internal error occurred"}), 500

# 可以在这里添加其他用户相关的路由，例如获取用户信息、更新用户信息等
# @user_bp.route('/profile', methods=['GET'])
# @jwt_required()
# def get_profile():
#     current_user_id = get_jwt_identity()
#     user = User.objects(id=current_user_id).first()
#     if not user:
#         return jsonify({"msg": "User not found"}), 404
#     # 返回用户信息的逻辑，注意不要泄露敏感数据如 password_hash
#     return jsonify(username=user.username, email=user.email, created_at=user.created_at), 200 