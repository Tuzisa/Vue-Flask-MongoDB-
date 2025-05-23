from .. import db
import datetime

class Item(db.Document):
    """商品模型"""
    title = db.StringField(required=True, max_length=100)
    description = db.StringField(required=True)
    price = db.FloatField(required=True, min_value=0)
    category = db.StringField(required=True, choices=[
        'electronics', 'clothing', 'books', 'furniture', 'other'
    ])
    images = db.ListField(db.StringField(), default=[])  # 存储图片路径或URL
    seller = db.ReferenceField('User', required=True)  # 引用用户模型
    created_at = db.DateTimeField(default=datetime.datetime.utcnow)
    updated_at = db.DateTimeField(default=datetime.datetime.utcnow)
    status = db.StringField(default='available', choices=[
        'available', 'reserved', 'sold'
    ])
    views = db.IntField(default=0)  # 浏览次数
    
    meta = {
        'collection': 'items',
        'indexes': [
            'title', 
            'category', 
            'seller', 
            'status',
            'created_at'
        ],
        'ordering': ['-created_at']  # 默认按创建时间倒序排列
    }
    
    def update_timestamp(self):
        """更新时间戳"""
        self.updated_at = datetime.datetime.utcnow()
        
    def __repr__(self):
        return f'<Item {self.title} by {self.seller.username}>' 