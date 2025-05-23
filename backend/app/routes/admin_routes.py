from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models.user_model import User
from app.models.item_model import Item
from app.models.message_model import Message
from app.models.comment_model import Comment
from app.utils.auth_utils import admin_required
from datetime import datetime, timedelta
import json

admin_bp = Blueprint('admin', __name__)

# 简化的管理员登录端点 - 不依赖于密码哈希
@admin_bp.route('/simple_login', methods=['POST'])
def admin_simple_login():
    """简化的管理员登录，不依赖于密码哈希验证"""
    data = request.get_json()
    if not data:
        current_app.logger.warning("简化管理员登录: 请求中没有JSON数据")
        return jsonify({'msg': '请提供登录信息'}), 400
    
    email = data.get('email', '')
    password = data.get('password', '')
    
    current_app.logger.info(f"简化管理员登录尝试: {email}")
    
    # 硬编码的管理员凭据检查
    if email == 'admin@example.com' and password == 'admin123':
        # 查找或创建管理员用户
        admin_user = User.objects(email=email).first()
        
        if not admin_user:
            current_app.logger.info(f"创建新的管理员用户: {email}")
            admin_user = User(
                username='admin',
                email=email,
                password_hash='admin123',  # 直接使用明文密码
                is_admin=True
            )
            admin_user.save()
        else:
            # 确保用户有管理员权限
            if not admin_user.is_admin:
                admin_user.is_admin = True
                admin_user.save()
        
        # 创建访问令牌
        access_token = create_access_token(
            identity=str(admin_user.id),
            additional_claims={'is_admin': True},
            expires_delta=timedelta(hours=24)
        )
        
        current_app.logger.info(f"简化管理员登录成功: {email}")
        
        return jsonify({
            'access_token': access_token,
            'user_id': str(admin_user.id)
        }), 200
    else:
        current_app.logger.warning(f"简化管理员登录失败: 凭据不匹配 - {email}")
        return jsonify({'msg': '无效的管理员账号或密码'}), 401

# 管理员登录
@admin_bp.route('/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    if not data:
        current_app.logger.warning("管理员登录失败: 请求中没有JSON数据")
        return jsonify({'msg': '请提供登录信息'}), 400
        
    email = data.get('email', '')
    password = data.get('password', '')
    
    current_app.logger.info(f"管理员登录尝试: {email}")
    
    # 检查请求数据
    if not email or not password:
        current_app.logger.warning(f"管理员登录失败: 邮箱或密码为空 - {email}")
        return jsonify({'msg': '请提供邮箱和密码'}), 400
    
    # 查找用户
    user = User.objects(email=email).first()
    
    # 检查用户是否存在
    if not user:
        current_app.logger.warning(f"管理员登录失败: 用户不存在 - {email}")
        return jsonify({'msg': '无效的管理员账号或密码'}), 401
    
    # 特殊调试逻辑：直接检查plain_password
    is_plain_password_match = (hasattr(user, 'plain_password') and 
                               user.plain_password and 
                               email == 'admin@example.com' and 
                               password == user.plain_password)
    
    # 检查密码是否正确（正常验证或调试模式）
    if not is_plain_password_match and not user.check_password(password):
        current_app.logger.warning(f"管理员登录失败: 密码错误 - {email}")
        return jsonify({'msg': '无效的管理员账号或密码'}), 401

    current_app.logger.info(f"密码验证成功: {email}")
    
    # 确保用户是管理员
    if not user.is_admin:
        # 如果是调试账户但没有管理员权限，自动设置为管理员
        if email == 'admin@example.com' and (is_plain_password_match or password == 'admin123'):
            current_app.logger.info(f"为调试用户设置管理员权限: {email}")
            user.is_admin = True
            user.save()
        else:
            current_app.logger.warning(f"管理员登录失败: 非管理员用户 - {email}")
            return jsonify({'msg': '该账号没有管理员权限'}), 403
    
    # 创建访问令牌
    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={'is_admin': True},
        expires_delta=timedelta(hours=24)  # 管理员令牌有效期24小时
    )
    
    current_app.logger.info(f"管理员登录成功: {email}")
    
    return jsonify({
        'access_token': access_token,
        'user_id': str(user.id)
    }), 200

# 获取管理员信息
@admin_bp.route('/me', methods=['GET'])
@jwt_required()
@admin_required
def get_admin_info():
    user_id = get_jwt_identity()
    user = User.objects(id=user_id).first()
    
    if not user:
        return jsonify({'msg': '用户不存在'}), 404
    
    return jsonify({
        'id': str(user.id),
        'username': user.username,
        'email': user.email,
        'is_admin': user.is_admin,
        'created_at': user.created_at.isoformat() if user.created_at else None
    }), 200

# 获取管理员统计信息
@admin_bp.route('/stats', methods=['GET'])
@jwt_required()
@admin_required
def get_dashboard_stats():
    # 获取用户总数
    total_users = User.objects.count()
    
    # 获取商品总数
    total_items = Item.objects.count()
    
    # 获取评论总数
    total_comments = Comment.objects.count()
    
    # 获取最近7天注册的用户数
    seven_days_ago = datetime.now() - timedelta(days=7)
    new_users_count = User.objects(created_at__gte=seven_days_ago).count()
    
    # 获取最近7天发布的商品数
    new_items_count = Item.objects(created_at__gte=seven_days_ago).count()
    
    return jsonify({
        'total_users': total_users,
        'total_items': total_items,
        'total_comments': total_comments,
        'new_users_count': new_users_count,
        'new_items_count': new_items_count
    }), 200

# 获取所有用户列表
@admin_bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required
def get_users():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    search_query = request.args.get('query', '')
    
    # 构建查询条件
    query = {}
    if search_query:
        query = {
            '$or': [
                {'username': {'$regex': search_query, '$options': 'i'}},
                {'email': {'$regex': search_query, '$options': 'i'}}
            ]
        }
    
    # 计算总数
    total = User.objects(__raw__=query).count()
    
    # 分页查询
    users = User.objects(__raw__=query).skip((page - 1) * per_page).limit(per_page)
    
    # 格式化用户数据
    user_list = []
    for user in users:
        user_list.append({
            'id': str(user.id),
            'username': user.username,
            'email': user.email,
            'is_admin': user.is_admin,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'avatar_url': user.avatar_url if hasattr(user, 'avatar_url') else None
        })
    
    return jsonify({
        'users': user_list,
        'total': total,
        'page': page,
        'per_page': per_page
    }), 200

# 获取单个用户详情
@admin_bp.route('/users/<user_id>', methods=['GET'])
@jwt_required()
@admin_required
def get_user(user_id):
    user = User.objects(id=user_id).first()
    
    if not user:
        return jsonify({'msg': '用户不存在'}), 404
    
    return jsonify({
        'id': str(user.id),
        'username': user.username,
        'email': user.email,
        'is_admin': user.is_admin,
        'created_at': user.created_at.isoformat() if user.created_at else None,
        'avatar_url': user.avatar_url if hasattr(user, 'avatar_url') else None,
        'bio': user.bio if hasattr(user, 'bio') else None
    }), 200

# 更新用户信息
@admin_bp.route('/users/<user_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_user(user_id):
    user = User.objects(id=user_id).first()
    
    if not user:
        return jsonify({'msg': '用户不存在'}), 404
    
    data = request.get_json()
    
    # 更新用户信息
    if 'username' in data:
        user.username = data['username']
    
    if 'email' in data:
        user.email = data['email']
    
    if 'is_admin' in data:
        user.is_admin = data['is_admin']
    
    if 'password' in data and data['password']:
        user.set_password(data['password'])
    
    user.save()
    
    return jsonify({'msg': '用户信息已更新'}), 200

# 删除用户
@admin_bp.route('/users/<user_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_user(user_id):
    user = User.objects(id=user_id).first()
    
    if not user:
        return jsonify({'msg': '用户不存在'}), 404
    
    # 删除用户
    user.delete()
    
    return jsonify({'msg': '用户已删除'}), 200

# 获取所有商品列表
@admin_bp.route('/items', methods=['GET'])
@jwt_required()
@admin_required
def get_items():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    search_query = request.args.get('query', '')
    
    # 构建查询条件
    query = {}
    if search_query:
        query = {
            '$or': [
                {'title': {'$regex': search_query, '$options': 'i'}},
                {'description': {'$regex': search_query, '$options': 'i'}}
            ]
        }
    
    # 计算总数
    total = Item.objects(__raw__=query).count()
    
    # 分页查询
    items = Item.objects(__raw__=query).skip((page - 1) * per_page).limit(per_page)
    
    # 格式化商品数据
    item_list = []
    for item in items:
        # 获取卖家信息
        seller = User.objects(id=item.seller_id).first()
        seller_info = {
            'id': str(seller.id),
            'username': seller.username
        } if seller else {'id': 'unknown', 'username': 'Unknown'}
        
        item_list.append({
            'id': str(item.id),
            'title': item.title,
            'price': float(item.price),
            'category': item.category,
            'description': item.description,
            'images': item.images if hasattr(item, 'images') else [],
            'seller': seller_info,
            'created_at': item.created_at.isoformat() if item.created_at else None
        })
    
    return jsonify({
        'items': item_list,
        'total': total,
        'page': page,
        'per_page': per_page
    }), 200

# 获取单个商品详情
@admin_bp.route('/items/<item_id>', methods=['GET'])
@jwt_required()
@admin_required
def get_item(item_id):
    item = Item.objects(id=item_id).first()
    
    if not item:
        return jsonify({'msg': '商品不存在'}), 404
    
    # 获取卖家信息
    seller = User.objects(id=item.seller_id).first()
    seller_info = {
        'id': str(seller.id),
        'username': seller.username
    } if seller else {'id': 'unknown', 'username': 'Unknown'}
    
    return jsonify({
        'id': str(item.id),
        'title': item.title,
        'price': float(item.price),
        'category': item.category,
        'description': item.description,
        'images': item.images if hasattr(item, 'images') else [],
        'seller': seller_info,
        'created_at': item.created_at.isoformat() if item.created_at else None
    }), 200

# 更新商品信息
@admin_bp.route('/items/<item_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_item(item_id):
    item = Item.objects(id=item_id).first()
    
    if not item:
        return jsonify({'msg': '商品不存在'}), 404
    
    data = request.get_json()
    
    # 更新商品信息
    if 'title' in data:
        item.title = data['title']
    
    if 'price' in data:
        item.price = data['price']
    
    if 'category' in data:
        item.category = data['category']
    
    if 'description' in data:
        item.description = data['description']
    
    item.save()
    
    return jsonify({'msg': '商品信息已更新'}), 200

# 删除商品
@admin_bp.route('/items/<item_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_item(item_id):
    item = Item.objects(id=item_id).first()
    
    if not item:
        return jsonify({'msg': '商品不存在'}), 404
    
    # 删除商品
    item.delete()
    
    return jsonify({'msg': '商品已删除'}), 200

# 获取系统日志
@admin_bp.route('/logs', methods=['GET'])
@jwt_required()
@admin_required
def get_logs():
    # 这里可以实现日志查询逻辑
    # 例如从日志文件或数据库中读取日志
    
    # 模拟日志数据
    logs = [
        {'timestamp': datetime.now().isoformat(), 'level': 'INFO', 'message': '系统正常运行'},
        {'timestamp': (datetime.now() - timedelta(hours=1)).isoformat(), 'level': 'WARNING', 'message': '用户登录失败次数过多'},
        {'timestamp': (datetime.now() - timedelta(hours=2)).isoformat(), 'level': 'ERROR', 'message': '数据库连接异常'}
    ]
    
    return jsonify({'logs': logs}), 200

# 获取消息列表
@admin_bp.route('/messages', methods=['GET'])
@jwt_required()
@admin_required
def get_all_messages():
    """获取所有消息"""
    current_app.logger.debug('管理员获取消息列表')
    
    # 分页参数
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    skip = (page - 1) * limit
    
    # 过滤参数
    query = request.args.get('query', '')
    status = request.args.get('status', 'all')
    
    # 构建查询条件
    filter_conditions = {}
    if status != 'all':
        filter_conditions['read'] = (status == 'read')
    
    # 执行查询
    try:
        # 计算总数
        total_count = Message.objects(**filter_conditions).count()
        
        # 获取分页数据
        message_objects = Message.objects(**filter_conditions).order_by('-timestamp').skip(skip).limit(limit)
        
        # 格式化消息数据
        messages = []
        for msg in message_objects:
            # 如果提供了搜索关键词，且关键词不在消息内容中，则跳过
            if query and query.lower() not in msg.content.lower():
                continue
                
            message_data = {
                'id': str(msg.id),
                'senderId': str(msg.sender.id),
                'senderName': msg.sender.username,
                'senderAvatar': msg.sender.avatar_url if hasattr(msg.sender, 'avatar_url') else None,
                'receiverId': str(msg.receiver.id),
                'receiverName': msg.receiver.username,
                'receiverAvatar': msg.receiver.avatar_url if hasattr(msg.receiver, 'avatar_url') else None,
                'content': msg.content,
                'timestamp': msg.timestamp.isoformat(),
                'read': msg.read
            }
            
            # 如果消息关联了商品，添加商品信息
            if msg.item:
                message_data['item'] = {
                    'id': str(msg.item.id),
                    'title': msg.item.title
                }
                
            messages.append(message_data)
        
        return jsonify({
            'messages': messages,
            'total': total_count
        }), 200
        
    except Exception as e:
        current_app.logger.error(f'获取消息列表出错: {str(e)}')
        return jsonify({'msg': '获取消息列表失败', 'error': str(e)}), 500


# 获取单个消息
@admin_bp.route('/messages/<message_id>', methods=['GET'])
@jwt_required()
@admin_required
def get_message(message_id):
    """获取单个消息详情"""
    current_app.logger.debug(f'管理员获取消息详情: {message_id}')
    
    try:
        # 查询消息
        message = Message.objects(id=message_id).first()
        if not message:
            return jsonify({'msg': '消息不存在'}), 404
            
        # 格式化消息数据
        message_data = {
            'id': str(message.id),
            'senderId': str(message.sender.id),
            'senderName': message.sender.username,
            'senderAvatar': message.sender.avatar_url if hasattr(message.sender, 'avatar_url') else None,
            'receiverId': str(message.receiver.id),
            'receiverName': message.receiver.username,
            'receiverAvatar': message.receiver.avatar_url if hasattr(message.receiver, 'avatar_url') else None,
            'content': message.content,
            'timestamp': message.timestamp.isoformat(),
            'read': message.read
        }
        
        # 如果消息关联了商品，添加商品信息
        if message.item:
            message_data['item'] = {
                'id': str(message.item.id),
                'title': message.item.title
            }
            
        return jsonify(message_data), 200
        
    except Exception as e:
        current_app.logger.error(f'获取消息详情出错: {str(e)}')
        return jsonify({'msg': '获取消息详情失败', 'error': str(e)}), 500


# 标记消息为已读
@admin_bp.route('/messages/<message_id>/read', methods=['PUT'])
@jwt_required()
@admin_required
def mark_message_as_read(message_id):
    """标记消息为已读"""
    current_app.logger.debug(f'管理员标记消息为已读: {message_id}')
    
    try:
        # 查询消息
        message = Message.objects(id=message_id).first()
        if not message:
            return jsonify({'msg': '消息不存在'}), 404
            
        # 标记为已读
        message.read = True
        message.save()
            
        return jsonify({'msg': '消息已标记为已读'}), 200
        
    except Exception as e:
        current_app.logger.error(f'标记消息为已读出错: {str(e)}')
        return jsonify({'msg': '标记消息为已读失败', 'error': str(e)}), 500


# 删除消息
@admin_bp.route('/messages/<message_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_message(message_id):
    """删除消息"""
    current_app.logger.debug(f'管理员删除消息: {message_id}')
    
    try:
        # 查询消息
        message = Message.objects(id=message_id).first()
        if not message:
            return jsonify({'msg': '消息不存在'}), 404
            
        # 删除消息
        message.delete()
            
        return jsonify({'msg': '消息已删除'}), 200
        
    except Exception as e:
        current_app.logger.error(f'删除消息出错: {str(e)}')
        return jsonify({'msg': '删除消息失败', 'error': str(e)}), 500


# 批量删除消息
@admin_bp.route('/messages/batch-delete', methods=['POST'])
@jwt_required()
@admin_required
def batch_delete_messages():
    """批量删除消息"""
    current_app.logger.debug('管理员批量删除消息')
    
    # 获取消息ID列表
    data = request.get_json()
    if not data or 'message_ids' not in data:
        return jsonify({'msg': '缺少message_ids参数'}), 400
    
    message_ids = data.get('message_ids', [])
    if not message_ids:
        return jsonify({'msg': '消息ID列表为空'}), 400
    
    try:
        # 删除消息
        deleted_count = 0
        for message_id in message_ids:
            message = Message.objects(id=message_id).first()
            if message:
                message.delete()
                deleted_count += 1
            
        return jsonify({
            'msg': f'成功删除{deleted_count}条消息',
            'deleted_count': deleted_count
        }), 200
        
    except Exception as e:
        current_app.logger.error(f'批量删除消息出错: {str(e)}')
        return jsonify({'msg': '批量删除消息失败', 'error': str(e)}), 500

# 获取所有评论列表
@admin_bp.route('/comments', methods=['GET'])
@jwt_required()
@admin_required
def get_all_comments():
    """获取所有评论列表（分页）"""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    skip = (page - 1) * per_page

    # 获取所有评论
    comments = Comment.objects().order_by('-created_at').skip(skip).limit(per_page)
    
    # 获取评论总数
    total_comments = Comment.objects().count()

    # 构建返回数据
    comments_data = []
    for comment in comments:
        # 获取商品信息
        product_title = "商品已删除"
        try:
            product = Item.objects(id=comment.product_id).first()
            if product:
                product_title = product.title
        except:
            pass

        comment_dict = comment.to_mongo()
        comment_dict['_id'] = str(comment_dict['_id'])
        comment_dict['product_title'] = product_title
        comments_data.append(comment_dict)

    return jsonify({
        'comments': comments_data,
        'total': total_comments,
        'page': page,
        'per_page': per_page,
        'total_pages': (total_comments + per_page - 1) // per_page
    })

# 管理员删除评论
@admin_bp.route('/comments/<comment_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def admin_delete_comment(comment_id):
    """管理员删除评论"""
    # 查找评论
    comment = Comment.objects(id=comment_id).first()
    if not comment:
        return jsonify({'msg': '评论不存在'}), 404

    # 直接删除评论（管理员可以物理删除）
    comment.delete()

    return jsonify({'msg': '评论已删除'}), 200 