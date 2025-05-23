from datetime import datetime
from mongoengine import Document, StringField, ReferenceField, DateTimeField, BooleanField

class Comment(Document):
    """评论模型"""
    product_id = StringField(required=True)  # 商品ID
    user_id = StringField(required=True)  # 评论用户ID
    username = StringField(required=True)  # 评论用户昵称
    avatar = StringField()  # 评论用户头像URL
    content = StringField(required=True)  # 评论内容
    parent_id = StringField()  # 父评论ID（如果是回复评论）
    is_deleted = BooleanField(default=False)  # 是否已删除
    created_at = DateTimeField(default=datetime.utcnow)  # 评论时间

    meta = {
        'collection': 'comments',
        'indexes': [
            'product_id',
            'user_id',
            'parent_id',
            ('product_id', '-created_at')
        ],
        'ordering': ['-created_at']
    } 