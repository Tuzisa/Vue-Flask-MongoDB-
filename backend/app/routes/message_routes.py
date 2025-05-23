from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.message_model import Message
from ..models.user_model import User
from ..models.item_model import Item
from mongoengine.errors import ValidationError, DoesNotExist

message_bp = Blueprint('message_bp', __name__)

@message_bp.route('/<user_id>', methods=['GET'])
@jwt_required()
def get_messages(user_id):
    """获取当前用户与指定用户之间的聊天记录"""
    current_user_id = get_jwt_identity()
    
    # 检查当前用户是否存在
    current_user = User.objects(id=current_user_id).first()
    if not current_user:
        return jsonify({"msg": "Current user not found"}), 404
    
    # 检查目标用户是否存在
    target_user = User.objects(id=user_id).first()
    if not target_user:
        return jsonify({"msg": "Target user not found"}), 404
    
    try:
        # 获取双方之间的对话记录
        messages = Message.objects(
            (Message.sender == current_user) & (Message.receiver == target_user) |
            (Message.sender == target_user) & (Message.receiver == current_user)
        ).order_by('timestamp')
        
        # 格式化消息
        result = []
        for msg in messages:
            message_data = {
                "id": str(msg.id),
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "is_sender": str(msg.sender.id) == current_user_id,
                "read": msg.read
            }
            
            # 如果消息与商品相关，添加商品信息
            if msg.item:
                message_data["item"] = {
                    "id": str(msg.item.id),
                    "title": msg.item.title
                }
            
            result.append(message_data)
        
        # 将收到的未读消息标记为已读
        unread_messages = Message.objects(
            (Message.sender == target_user) & 
            (Message.receiver == current_user) &
            (Message.read == False)
        )
        for msg in unread_messages:
            msg.mark_as_read()
        
        return jsonify({
            "messages": result,
            "user": {
                "id": str(target_user.id),
                "username": target_user.username
            }
        }), 200
    except Exception as e:
        print(f"Error fetching messages: {e}")
        return jsonify({"msg": "An internal error occurred"}), 500

@message_bp.route('/send', methods=['POST'])
@jwt_required()
def send_message():
    """发送消息"""
    current_user_id = get_jwt_identity()
    
    # 检查当前用户是否存在
    current_user = User.objects(id=current_user_id).first()
    if not current_user:
        return jsonify({"msg": "Current user not found"}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({"msg": "Missing JSON in request"}), 400
    
    # 检查必填字段
    if 'receiver_id' not in data or 'content' not in data:
        return jsonify({"msg": "Missing receiver_id or content"}), 400
    
    # 检查接收者是否存在
    receiver = User.objects(id=data.get('receiver_id')).first()
    if not receiver:
        return jsonify({"msg": "Receiver not found"}), 404
    
    try:
        # 创建新消息
        new_message = Message(
            sender=current_user,
            receiver=receiver,
            content=data.get('content')
        )
        
        # 如果指定了商品，添加商品引用
        if 'item_id' in data and data.get('item_id'):
            item = Item.objects(id=data.get('item_id')).first()
            if item:
                new_message.item = item
        
        new_message.save()
        
        # 返回消息ID，用于前端确认消息已发送
        return jsonify({
            "msg": "Message sent successfully",
            "message_id": str(new_message.id),
            "timestamp": new_message.timestamp.isoformat()
        }), 201
    except ValidationError as e:
        return jsonify({"msg": "Validation error", "errors": str(e)}), 400
    except Exception as e:
        print(f"Error sending message: {e}")
        return jsonify({"msg": "An internal error occurred"}), 500

@message_bp.route('/unread/count', methods=['GET'])
@jwt_required()
def get_unread_count():
    """获取当前用户的未读消息数量"""
    current_user_id = get_jwt_identity()
    
    # 检查当前用户是否存在
    current_user = User.objects(id=current_user_id).first()
    if not current_user:
        return jsonify({"msg": "Current user not found"}), 404
    
    try:
        # 查询未读消息数量
        unread_count = Message.objects(
            (Message.receiver == current_user) &
            (Message.read == False)
        ).count()
        
        # 按发送者分组统计未读消息
        pipeline = [
            {
                '$match': {
                    'receiver': current_user.id,
                    'read': False
                }
            },
            {
                '$group': {
                    '_id': '$sender',
                    'count': {'$sum': 1},
                    'last_message': {'$last': '$content'},
                    'last_timestamp': {'$last': '$timestamp'}
                }
            }
        ]
        
        unread_by_sender = []
        for result in Message.objects.aggregate(pipeline):
            sender = User.objects(id=result['_id']).first()
            if sender:
                unread_by_sender.append({
                    "sender_id": str(sender.id),
                    "sender_username": sender.username,
                    "count": result['count'],
                    "last_message": result['last_message'],
                    "last_timestamp": result['last_timestamp'].isoformat()
                })
        
        return jsonify({
            "total_unread": unread_count,
            "unread_by_sender": unread_by_sender
        }), 200
    except Exception as e:
        print(f"Error fetching unread count: {e}")
        return jsonify({"msg": "An internal error occurred"}), 500

@message_bp.route('/contacts', methods=['GET'])
@jwt_required()
def get_contacts():
    """获取当前用户的联系人列表"""
    current_user_id = get_jwt_identity()
    
    # 检查当前用户是否存在
    current_user = User.objects(id=current_user_id).first()
    if not current_user:
        return jsonify({"msg": "Current user not found"}), 404
    
    try:
        # 查询与当前用户有过对话的所有用户
        # 先找出当前用户发送或接收的所有消息
        sent_messages = Message.objects(sender=current_user)
        received_messages = Message.objects(receiver=current_user)
        
        # 提取这些消息中涉及的用户ID
        contact_ids = set()
        
        for msg in sent_messages:
            contact_ids.add(str(msg.receiver.id))
        
        for msg in received_messages:
            contact_ids.add(str(msg.sender.id))
        
        # 获取这些用户的详细信息
        contacts = []
        for user_id in contact_ids:
            user = User.objects(id=user_id).first()
            if not user:
                continue
                
            # 获取最后一条消息
            last_message = Message.objects(
                (Message.sender == current_user) & (Message.receiver == user) |
                (Message.sender == user) & (Message.receiver == current_user)
            ).order_by('-timestamp').first()
            
            # 获取未读消息数量
            unread_count = Message.objects(
                (Message.sender == user) &
                (Message.receiver == current_user) &
                (Message.read == False)
            ).count()
            
            if last_message:
                contacts.append({
                    "user_id": str(user.id),
                    "username": user.username,
                    "last_message": last_message.content,
                    "last_timestamp": last_message.timestamp.isoformat(),
                    "unread_count": unread_count
                })
        
        # 按最后消息时间排序
        contacts.sort(key=lambda x: x['last_timestamp'], reverse=True)
        
        return jsonify({
            "contacts": contacts
        }), 200
    except Exception as e:
        print(f"Error fetching contacts: {e}")
        return jsonify({"msg": "An internal error occurred"}), 500 