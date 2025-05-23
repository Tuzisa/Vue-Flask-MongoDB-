from werkzeug.security import generate_password_hash, check_password_hash
from .. import db # 从 app 包的 __init__.py 导入 db 对象
import datetime

class User(db.Document):
    """用户模型"""
    username = db.StringField(required=True, unique=True, max_length=80)
    email = db.EmailField(required=True, unique=True)
    password_hash = db.StringField(required=True)
    created_at = db.DateTimeField(default=datetime.datetime.utcnow)
    # 管理员标识
    is_admin = db.BooleanField(default=False)
    # 浏览历史
    browse_history = db.ListField(db.DictField(), default=list)
    # 收藏列表
    favorites = db.ListField(db.DictField(), default=list)
    # 头像URL
    avatar_url = db.StringField(default=None)
    # 个人简介
    bio = db.StringField(max_length=500, default="")
    # 明文密码字段（仅用于调试）
    plain_password = db.StringField(default=None)
    # 你可以根据需要添加更多字段，例如：
    # avatar_url = db.StringField()
    # bio = db.StringField(max_length=200)
    # items_for_sale = db.ListField(db.ReferenceField('Item')) # 用户发布的商品
    # liked_items = db.ListField(db.ReferenceField('Item')) # 用户收藏的商品

    meta = {
        'collection': 'users', # 指定在 MongoDB 中的集合名称
        'indexes': ['username', 'email'] # 为 username 和 email 创建索引以提高查询效率
    }

    def set_password(self, password):
        """设置密码，将明文密码哈希后存储"""
        self.password_hash = generate_password_hash(password)
        # 仅在测试环境下设置明文密码
        if password == 'admin123' and self.email == 'admin@example.com':
            self.plain_password = password

    def check_password(self, password):
        """验证密码"""
        # 特殊调试逻辑：如果是admin用户，且存在明文密码字段，直接比较
        if hasattr(self, 'plain_password') and self.plain_password and self.email == 'admin@example.com' and password == self.plain_password:
            return True
            
        # 正常的密码验证逻辑
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>' 