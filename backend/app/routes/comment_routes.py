from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.comment import Comment
from app.models.user_model import User
from bson import ObjectId

comment_bp = Blueprint('comment', __name__)

@comment_bp.route('/products/<product_id>/comments', methods=['GET'])
def get_comments(product_id):
    """获取商品评论列表"""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    skip = (page - 1) * per_page

    # 获取主评论（没有parent_id的评论）
    parent_comments = Comment.objects(
        product_id=product_id,
        parent_id=None
    ).order_by('-created_at').skip(skip).limit(per_page)

    # 获取这些主评论的所有回复
    parent_ids = [str(comment.id) for comment in parent_comments]
    replies = Comment.objects(product_id=product_id, parent_id__in=parent_ids)
    
    # 将回复按父评论ID分组
    replies_dict = {}
    for reply in replies:
        if reply.parent_id not in replies_dict:
            replies_dict[reply.parent_id] = []
        replies_dict[reply.parent_id].append(reply.to_mongo())

    # 构建返回数据
    comments_data = []
    for comment in parent_comments:
        comment_dict = comment.to_mongo()
        comment_dict['replies'] = [
            {**reply, '_id': str(reply['_id'])}
            for reply in replies_dict.get(str(comment.id), [])
        ]
        comment_dict['_id'] = str(comment_dict['_id'])
        comments_data.append(comment_dict)

    # 获取评论总数（主评论）
    total_comments = Comment.objects(product_id=product_id, parent_id=None).count()

    return jsonify({
        'comments': comments_data,
        'total': total_comments,
        'page': page,
        'per_page': per_page,
        'total_pages': (total_comments + per_page - 1) // per_page
    })

@comment_bp.route('/products/<product_id>/comments', methods=['POST'])
@jwt_required()
def create_comment(product_id):
    """创建评论"""
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data or 'content' not in data:
        return jsonify({'msg': '评论内容不能为空'}), 400

    # 获取用户信息
    user = User.objects(id=user_id).first()
    if not user:
        return jsonify({'msg': '用户不存在'}), 404

    # 创建评论
    comment = Comment(
        product_id=product_id,
        user_id=str(user.id),
        username=user.username,
        avatar=user.avatar if hasattr(user, 'avatar') else None,
        content=data['content'],
        parent_id=data.get('parent_id')  # 如果是回复评论，则包含父评论ID
    )
    comment.save()

    return jsonify({
        'msg': '评论成功',
        'comment': {
            'id': str(comment.id),
            'content': comment.content,
            'username': comment.username,
            'avatar': comment.avatar,
            'created_at': comment.created_at.isoformat(),
            'parent_id': comment.parent_id
        }
    }), 201

@comment_bp.route('/comments/<comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(comment_id):
    """删除评论"""
    user_id = get_jwt_identity()
    
    # 查找评论
    comment = Comment.objects(id=comment_id).first()
    if not comment:
        return jsonify({'msg': '评论不存在'}), 404

    # 验证是否是评论作者
    if str(comment.user_id) != str(user_id):
        return jsonify({'msg': '无权删除此评论'}), 403

    # 软删除评论
    comment.is_deleted = True
    comment.content = "该评论已被用户删除"
    comment.save()

    return jsonify({'msg': '评论已删除'}), 200 