from mongoengine import Document, StringField, ReferenceField, DateTimeField, BooleanField
from datetime import datetime
from .user_model import User
from .item_model import Item

class Comment(Document):
    """评论模型"""
    user_id = StringField(required=True)  # 评论用户ID
    username = StringField(required=True)  # 评论用户名
    product_id = StringField(required=True)  # 商品ID
    content = StringField(required=True)  # 评论内容
    parent_id = StringField()  # 父评论ID（用于回复）
    created_at = DateTimeField(default=datetime.utcnow)  # 创建时间
    is_deleted = BooleanField(default=False)  # 是否被用户删除（软删除）

    meta = {
        'collection': 'comments',
        'indexes': [
            'user_id',
            'product_id',
            'parent_id',
            'created_at'
        ],
        'ordering': ['-created_at']
    }

    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': str(self.id),
            'user_id': self.user_id,
            'username': self.username,
            'product_id': self.product_id,
            'content': self.content,
            'parent_id': self.parent_id,
            'created_at': self.created_at.isoformat(),
            'is_deleted': self.is_deleted
        } 