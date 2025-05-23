from flask_socketio import emit, join_room, leave_room
from flask_jwt_extended import jwt_required, get_jwt_identity, decode_token
from flask import request, current_app
from .models.message_model import Message
from .models.user_model import User
from .models.item_model import Item
import datetime
import json
import jwt

# 使用内存存储用户会话信息，而不是依赖 Redis
# 存储用户会话信息的字典，key是用户ID，value是会话ID
user_sessions = {}

def register_handlers(socketio):
    """注册所有Socket.IO事件处理函数"""
    
    @socketio.on('connect')
    def handle_connect():
        """处理客户端连接"""
        print('Client connected', request.sid)
        emit('connect_response', {'status': 'connected', 'sid': request.sid})
        
    @socketio.on('disconnect')
    def handle_disconnect():
        """处理客户端断开连接"""
        print('Client disconnected', request.sid)
        
        # 移除用户的会话信息
        for user_id, session_id in list(user_sessions.items()):
            if session_id == request.sid:
                del user_sessions[user_id]
                print(f"User {user_id} logged out")
                break
    
    @socketio.on('authenticate')
    def handle_authenticate(data):
        """处理用户认证"""
        print("Authentication attempt with data:", data)
        token = data.get('token')
        if not token:
            emit('authentication_error', {'message': 'No token provided'})
            return
        
        try:
            # 验证JWT token
            # 从配置中获取密钥
            jwt_secret_key = current_app.config.get('JWT_SECRET_KEY')
            if not jwt_secret_key:
                emit('authentication_error', {'message': 'JWT secret not configured'})
                return
                
            try:
                # 使用Flask-JWT-Extended的decode_token
                payload = decode_token(token)
                user_id = payload['sub']  # JWT中的用户ID
                
                # 检查令牌有效期
                if 'exp' in payload and datetime.datetime.now().timestamp() > payload['exp']:
                    emit('authentication_error', {'message': 'Token has expired'})
                    return
            except Exception as e:
                # 尝试使用PyJWT库直接解析
                try:
                    payload = jwt.decode(
                        token, 
                        jwt_secret_key, 
                        algorithms=['HS256'],
                        options={"verify_signature": True}
                    )
                    user_id = payload['sub']
                except Exception as jwt_error:
                    print(f"JWT decode error: {jwt_error}")
                    emit('authentication_error', {'message': f'Invalid token: {str(jwt_error)}'})
                    return
            
            # 检查用户是否存在
            user = User.objects(id=user_id).first()
            if not user:
                emit('authentication_error', {'message': 'User not found'})
                return
            
            # 如果该用户已经有一个活跃会话，通知旧会话
            if user_id in user_sessions:
                old_session = user_sessions[user_id]
                if old_session != request.sid:  # 如果不是同一个会话ID
                    # 通知旧会话它已被替代
                    try:
                        emit('session_expired', {'message': 'Your session has been taken over by another login'}, room=old_session)
                    except Exception as e:
                        print(f"Error notifying old session: {e}")
            
            # 记录用户的会话ID
            user_sessions[user_id] = request.sid
            
            # 加入以用户ID命名的房间，用于私聊
            join_room(user_id)
            
            emit('authenticated', {
                'user_id': user_id,
                'username': user.username
            })
            
            print(f"User {user.username} authenticated with socket ID {request.sid}")
        except Exception as e:
            print(f"Authentication error: {e}")
            emit('authentication_error', {'message': f'Authentication failed: {str(e)}'})
    
    @socketio.on('send_message')
    def handle_send_message(data):
        """处理发送消息"""
        try:
            # 检查必要数据
            if not all(k in data for k in ('sender_id', 'receiver_id', 'content')):
                emit('error', {'message': 'Missing required fields'})
                return
            
            sender_id = data['sender_id']
            receiver_id = data['receiver_id']
            content = data['content']
            
            # 安全检查：确保发送方ID与当前认证的用户匹配
            for user_id, session_id in user_sessions.items():
                if session_id == request.sid and user_id != sender_id:
                    emit('error', {'message': 'You can only send messages as yourself'})
                    return
            
            # 查找发送者和接收者
            sender = User.objects(id=sender_id).first()
            receiver = User.objects(id=receiver_id).first()
            
            if not sender or not receiver:
                emit('error', {'message': 'Sender or receiver not found'})
                return
            
            # 创建新消息
            new_message = Message(
                sender=sender,
                receiver=receiver,
                content=content
            )
            
            # 如果指定了商品，添加商品引用
            if 'item_id' in data and data['item_id']:
                item = Item.objects(id=data['item_id']).first()
                if item:
                    new_message.item = item
            
            new_message.save()
            
            # 准备消息数据
            message_data = {
                'id': str(new_message.id),
                'sender_id': sender_id,
                'receiver_id': receiver_id,
                'content': content,
                'timestamp': new_message.timestamp.isoformat(),
                'read': False
            }
            
            if hasattr(new_message, 'item') and new_message.item:
                message_data['item'] = {
                    'id': str(new_message.item.id),
                    'title': new_message.item.title
                }
            
            # 发送给发送者确认
            emit('message_sent', message_data)
            
            # 查看接收者是否在线
            if receiver_id in user_sessions:
                # 发送到接收者的房间
                emit('new_message', message_data, room=receiver_id)
            
            print(f"Message sent from {sender.username} to {receiver.username}")
        except Exception as e:
            print(f"Error sending message: {e}")
            emit('error', {'message': f'Failed to send message: {str(e)}'})
    
    @socketio.on('mark_read')
    def handle_mark_read(data):
        """标记消息为已读"""
        try:
            if 'message_id' not in data:
                emit('error', {'message': 'Missing message_id'})
                return
            
            message_id = data['message_id']
            message = Message.objects(id=message_id).first()
            
            if not message:
                emit('error', {'message': 'Message not found'})
                return
            
            # 安全检查：确保只有接收者可以标记消息为已读
            current_user_id = None
            for user_id, session_id in user_sessions.items():
                if session_id == request.sid:
                    current_user_id = user_id
                    break
            
            if not current_user_id or str(message.receiver.id) != current_user_id:
                emit('error', {'message': 'You can only mark messages sent to you as read'})
                return
            
            # 标记为已读
            message.read = True
            message.save()
            
            # 通知发送者消息已读
            if str(message.sender.id) in user_sessions:
                emit('message_read', {
                    'message_id': message_id,
                    'read_at': datetime.datetime.utcnow().isoformat()
                }, room=str(message.sender.id))
            
            emit('marked_read', {'message_id': message_id})
        except Exception as e:
            print(f"Error marking message as read: {e}")
            emit('error', {'message': f'Failed to mark message as read: {str(e)}'})
    
    @socketio.on('typing')
    def handle_typing(data):
        """处理用户正在输入的通知"""
        try:
            if not all(k in data for k in ('sender_id', 'receiver_id')):
                return
            
            sender_id = data['sender_id']
            receiver_id = data['receiver_id']
            
            # 安全检查：确保发送方ID与当前认证的用户匹配
            current_user_id = None
            for user_id, session_id in user_sessions.items():
                if session_id == request.sid:
                    current_user_id = user_id
                    break
            
            if not current_user_id or current_user_id != sender_id:
                return
            
            # 检查接收者是否在线
            if receiver_id in user_sessions:
                emit('user_typing', {
                    'sender_id': sender_id
                }, room=receiver_id)
        except Exception as e:
            print(f"Error handling typing notification: {e}")
    
    @socketio.on('error')
    def handle_error(error):
        """处理Socket.IO错误"""
        print(f"Socket.IO error: {error}")
    
    print("SocketIO event handlers registered")