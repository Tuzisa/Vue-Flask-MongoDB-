from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.item_model import Item
from ..models.user_model import User
import json

analytics_bp = Blueprint('analytics_bp', __name__)

@analytics_bp.route('/popular-categories', methods=['GET'])
def get_popular_categories():
    """统计商品分类数量"""
    try:
        # 使用MongoDB聚合$group统计商品分类数量
        pipeline = [
            {
                '$group': {
                    '_id': '$category',
                    'count': {'$sum': 1}
                }
            },
            {
                '$sort': {'count': -1}  # 按数量降序排序
            }
        ]
        
        results = list(Item.objects.aggregate(pipeline))
        
        # 格式化结果
        categories = []
        for result in results:
            categories.append({
                "category": result['_id'],
                "count": result['count']
            })
        
        return jsonify({
            "categories": categories
        }), 200
    except Exception as e:
        print(f"Error getting popular categories: {e}")
        return jsonify({"msg": "An internal error occurred"}), 500

# 假设有一个浏览记录模型或在用户模型中存储浏览历史
@analytics_bp.route('/browse-not-bought', methods=['GET'])
@jwt_required()
def get_browse_not_bought():
    """返回当前用户浏览过但未购买的商品"""
    current_user_id = get_jwt_identity()
    
    # 检查当前用户是否存在
    current_user = User.objects(id=current_user_id).first()
    if not current_user:
        return jsonify({"msg": "User not found"}), 404
    
    try:
        # 这里假设我们有另一个集合来存储用户浏览记录
        # 由于我们没有实际的浏览记录模型，这里用一个模拟数据来演示
        # 实际实现中，你需要创建一个浏览记录模型，并基于该模型查询数据
        
        # 模拟数据 - 这里简单地返回一些用户可能感兴趣的商品
        # 实际实现应该查询数据库中的浏览记录
        
        # 查询用户未发布的商品（模拟浏览过的商品）
        items = Item.objects(seller__ne=current_user).limit(5)
        
        result = []
        for item in items:
            result.append({
                "id": str(item.id),
                "title": item.title,
                "price": item.price,
                "category": item.category,
                "image": item.images[0] if item.images else None
            })
        
        return jsonify({
            "recommended_items": result
        }), 200
    except Exception as e:
        print(f"Error getting browse-not-bought recommendations: {e}")
        return jsonify({"msg": "An internal error occurred"}), 500

@analytics_bp.route('/user-stats', methods=['GET'])
@jwt_required()
def get_user_stats():
    """获取当前用户的统计信息"""
    current_user_id = get_jwt_identity()
    
    # 检查当前用户是否存在
    current_user = User.objects(id=current_user_id).first()
    if not current_user:
        return jsonify({"msg": "User not found"}), 404
    
    try:
        # 统计用户发布的商品数量
        items_count = Item.objects(seller=current_user).count()
        
        # 统计用户发布的商品按状态分组
        pipeline = [
            {
                '$match': {'seller': current_user.id}
            },
            {
                '$group': {
                    '_id': '$status',
                    'count': {'$sum': 1}
                }
            }
        ]
        
        status_counts = {}
        for result in Item.objects.aggregate(pipeline):
            status_counts[result['_id']] = result['count']
        
        # 获取总浏览量
        total_views = Item.objects(seller=current_user).sum('views')
        
        # 获取收藏数量
        favorites_count = 0
        if hasattr(current_user, 'favorites') and current_user.favorites:
            favorites_count = len(current_user.favorites)
        
        return jsonify({
            "user": {
                "id": str(current_user.id),
                "username": current_user.username,
                "joined_at": current_user.created_at.isoformat()
            },
            "items_count": items_count,
            "status_counts": status_counts,
            "total_views": total_views,
            "favorites_count": favorites_count
        }), 200
    except Exception as e:
        print(f"Error getting user stats: {e}")
        return jsonify({"msg": "An internal error occurred"}), 500 