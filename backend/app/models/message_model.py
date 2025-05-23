from .. import db
import datetime

class Message(db.Document):
    """消息模型，用于存储用户之间的聊天记录"""
    sender = db.ReferenceField('User', required=True)  # 发送者
    receiver = db.ReferenceField('User', required=True)  # 接收者
    content = db.StringField(required=True)  # 消息内容
    timestamp = db.DateTimeField(default=datetime.datetime.utcnow)  # 发送时间
    read = db.BooleanField(default=False)  # 消息是否已读
    item = db.ReferenceField('Item', required=False)  # 相关联的商品（可选）
    
    meta = {
        'collection': 'messages',
        'indexes': [
            ('sender', 'receiver', 'timestamp'),  # 联合索引，用于查询两个用户之间的对话
            'timestamp'
        ],
        'ordering': ['timestamp']  # 默认按时间正序排列
    }
    
    def mark_as_read(self):
        """将消息标记为已读"""
        self.read = True
        self.save()
        
    def __repr__(self):
        return f'<Message from {self.sender.username} to {self.receiver.username}>' 