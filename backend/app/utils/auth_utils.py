from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt

# 管理员权限验证装饰器
def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # 验证JWT令牌
        verify_jwt_in_request()
        
        # 获取JWT中的claims
        claims = get_jwt()
        
        # 检查是否是管理员
        if not claims.get('is_admin', False):
            return jsonify({'msg': '需要管理员权限'}), 403
        
        # 如果是管理员，继续执行原函数
        return fn(*args, **kwargs)
    
    return wrapper 