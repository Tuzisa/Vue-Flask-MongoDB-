from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.item_model import Item
from ..models.user_model import User
from mongoengine.errors import ValidationError, DoesNotExist
import datetime
import os
import uuid
from werkzeug.utils import secure_filename
import json

item_bp = Blueprint('item_bp', __name__)

# 设置允许的图片文件扩展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
# 设置上传文件夹
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'uploads')

# 确保上传文件夹存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@item_bp.route('', methods=['POST'])
@jwt_required()
def create_item():
    """创建新商品"""
    current_user_id = get_jwt_identity()
    user = User.objects(id=current_user_id).first()
    
    if not user:
        return jsonify({"msg": "User not found"}), 404
    
    # 检查内容类型
    content_type = request.content_type or ''
    
    # 处理JSON请求
    if 'application/json' in content_type:
        data = request.get_json()
        if not data:
            return jsonify({"msg": "Missing JSON in request"}), 400
        
        # 检查必填字段
        required_fields = ['title', 'description', 'price', 'category']
        for field in required_fields:
            if field not in data:
                return jsonify({"msg": f"Missing {field}"}), 400
        
        try:
            # 创建新商品
            new_item = Item(
                title=data.get('title'),
                description=data.get('description'),
                price=float(data.get('price')),
                category=data.get('category'),
                seller=user,
                images=data.get('images', [])
            )
            new_item.save()
            
            return jsonify({
                "msg": "Item created successfully",
                "item_id": str(new_item.id)
            }), 201
        except ValidationError as e:
            return jsonify({"msg": "Validation error", "errors": str(e)}), 400
        except Exception as e:
            print(f"Error creating item: {e}")
            return jsonify({"msg": "An internal error occurred"}), 500
    
    # 处理multipart/form-data请求
    elif 'multipart/form-data' in content_type:
        try:
            # 获取表单数据
            title = request.form.get('title')
            description = request.form.get('description')
            price = request.form.get('price')
            category = request.form.get('category')
            
            # 检查必填字段
            if not all([title, description, price, category]):
                return jsonify({"msg": "Missing required fields"}), 400
            
            # 处理图片上传
            image_paths = []
            if 'images' in request.files:
                files = request.files.getlist('images')
                for file in files:
                    if file and allowed_file(file.filename):
                        # 生成安全的文件名
                        filename = secure_filename(file.filename)
                        # 添加UUID前缀避免文件名冲突
                        unique_filename = f"{uuid.uuid4()}_{filename}"
                        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
                        
                        # 保存文件
                        file.save(file_path)
                        
                        # 存储相对路径
                        relative_path = f"/static/uploads/{unique_filename}"
                        image_paths.append(relative_path)
            
            # 创建新商品
            new_item = Item(
                title=title,
                description=description,
                price=float(price),
                category=category,
                seller=user,
                images=image_paths
            )
            new_item.save()
            
            return jsonify({
                "msg": "Item created successfully",
                "item_id": str(new_item.id),
                "images": image_paths
            }), 201
        except ValidationError as e:
            return jsonify({"msg": "Validation error", "errors": str(e)}), 400
        except Exception as e:
            print(f"Error creating item with form data: {e}")
            return jsonify({"msg": "An internal error occurred"}), 500
    
    else:
        return jsonify({"msg": "Unsupported media type"}), 415

@item_bp.route('', methods=['GET'])
def get_items():
    """获取商品列表，支持搜索和筛选"""
    # 获取查询参数
    keyword = request.args.get('keyword', '')
    category = request.args.get('category', '')
    min_price = request.args.get('min_price', '')
    max_price = request.args.get('max_price', '')
    sort = request.args.get('sort', 'newest')  # 排序方式: newest, price_asc, price_desc, views
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 12))
    exclude_id = request.args.get('excludeId', '')  # 排除特定ID的商品（用于推荐时排除当前商品）
    seller_id = request.args.get('seller_id', '')  # 按卖家ID过滤
    
    # 打印接收到的参数，便于调试
    print(f"查询参数: keyword={keyword}, category={category}, min_price={min_price}, max_price={max_price}, sort={sort}")
    
    # 构建查询条件
    query = {}
    if keyword:
        # 使用正则表达式进行模糊搜索（标题或描述中包含搜索词）
        query['$or'] = [
            {'title': {'$regex': keyword, '$options': 'i'}},
            {'description': {'$regex': keyword, '$options': 'i'}}
        ]
    
    if category:
        query['category'] = category
    
    # 价格范围筛选
    price_query = {}
    if min_price:
        try:
            min_price_float = float(min_price)
            price_query['$gte'] = min_price_float
            print(f"设置最低价格筛选: {min_price_float}")
        except (ValueError, TypeError):
            print(f"无效的最低价格值: {min_price}")
            pass
    
    if max_price:
        try:
            max_price_float = float(max_price)
            price_query['$lte'] = max_price_float
            print(f"设置最高价格筛选: {max_price_float}")
        except (ValueError, TypeError):
            print(f"无效的最高价格值: {max_price}")
            pass
    
    if price_query:
        query['price'] = price_query
        print(f"价格筛选条件: {price_query}")
    
    # 排除特定ID的商品
    if exclude_id:
        query['id'] = {'$ne': exclude_id}
    
    # 按卖家ID过滤
    if seller_id:
        query['seller'] = seller_id
    
    # 默认只显示可用的商品，除非明确指定了卖家ID
    if not seller_id:
        query['status'] = 'available'
    
    print(f"最终查询条件: {query}")
    
    # 确定排序方式
    if sort == 'newest':
        sort_field = '-created_at'  # 最新发布
    elif sort == 'price_asc':
        sort_field = '+price'  # 价格从低到高
    elif sort == 'price_desc':
        sort_field = '-price'  # 价格从高到低
    elif sort == 'views':
        sort_field = '-views'  # 浏览量
    else:
        sort_field = '-created_at'  # 默认按创建时间排序
    
    try:
        # 执行查询
        items = Item.objects(__raw__=query).order_by(sort_field)
        
        # 获取总数
        total_count = items.count()
        
        # 分页
        paginated_items = items.skip((page - 1) * limit).limit(limit)
        
        # 格式化结果
        result = []
        for item in paginated_items:
            seller_data = {
                "id": str(item.seller.id),
                "username": item.seller.username
            }
            
            result.append({
                "id": str(item.id),
                "title": item.title,
                "description": item.description,
                "price": item.price,
                "category": item.category,
                "images": item.images,
                "seller": seller_data,
                "created_at": item.created_at.isoformat(),
                "updated_at": item.updated_at.isoformat(),
                "status": item.status,
                "views": item.views
            })
        
        # 返回分页信息和结果
        return jsonify({
            "total": total_count,
            "page": page,
            "limit": limit,
            "items": result
        }), 200
    except Exception as e:
        print(f"Error fetching items: {e}")
        return jsonify({"msg": "An internal error occurred"}), 500

@item_bp.route('/<item_id>', methods=['GET'])
def get_item(item_id):
    """获取单个商品的详细信息"""
    try:
        item = Item.objects(id=item_id).first()
        
        if not item:
            return jsonify({"msg": "Item not found"}), 404
        
        # 增加浏览次数
        item.views += 1
        item.save()
        
        # 格式化返回结果
        result = {
            "id": str(item.id),
            "title": item.title,
            "description": item.description,
            "price": item.price,
            "category": item.category,
            "images": item.images,
            "seller": {
                "id": str(item.seller.id),
                "username": item.seller.username
            },
            "created_at": item.created_at.isoformat(),
            "updated_at": item.updated_at.isoformat(),
            "status": item.status,
            "views": item.views
        }
        
        return jsonify(result), 200
    except DoesNotExist:
        return jsonify({"msg": "Item not found"}), 404
    except Exception as e:
        print(f"Error fetching item: {e}")
        return jsonify({"msg": "An internal error occurred"}), 500

@item_bp.route('/<item_id>', methods=['PUT'])
@jwt_required()
def update_item(item_id):
    """更新商品信息"""
    current_user_id = get_jwt_identity()
    
    try:
        item = Item.objects(id=item_id).first()
        
        if not item:
            return jsonify({"msg": "Item not found"}), 404
        
        # 检查是否是商品卖家
        if str(item.seller.id) != current_user_id:
            return jsonify({"msg": "Unauthorized: You are not the seller of this item"}), 403
        
        # 检查内容类型
        content_type = request.content_type or ''
        
        # 处理JSON请求
        if 'application/json' in content_type:
            data = request.get_json()
            if not data:
                return jsonify({"msg": "Missing JSON in request"}), 400
            
            # 更新允许的字段
            if 'title' in data:
                item.title = data['title']
            if 'description' in data:
                item.description = data['description']
            if 'price' in data:
                item.price = float(data['price'])
            if 'category' in data:
                item.category = data['category']
            if 'images' in data:
                item.images = data['images']
            if 'status' in data and data['status'] in ['available', 'reserved', 'sold']:
                item.status = data['status']
        
        # 处理multipart/form-data请求
        elif 'multipart/form-data' in content_type:
            # 获取表单数据
            if 'title' in request.form:
                item.title = request.form.get('title')
            if 'description' in request.form:
                item.description = request.form.get('description')
            if 'price' in request.form:
                item.price = float(request.form.get('price'))
            if 'category' in request.form:
                item.category = request.form.get('category')
            if 'status' in request.form and request.form.get('status') in ['available', 'reserved', 'sold']:
                item.status = request.form.get('status')
            
            # 处理已有图片
            existing_images = []
            if 'existing_images' in request.form:
                try:
                    existing_images = json.loads(request.form.get('existing_images'))
                except:
                    existing_images = []
            
            # 处理新上传的图片
            new_image_paths = []
            if 'images' in request.files:
                files = request.files.getlist('images')
                for file in files:
                    if file and allowed_file(file.filename):
                        # 生成安全的文件名
                        filename = secure_filename(file.filename)
                        # 添加UUID前缀避免文件名冲突
                        unique_filename = f"{uuid.uuid4()}_{filename}"
                        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
                        
                        # 保存文件
                        file.save(file_path)
                        
                        # 存储相对路径
                        relative_path = f"/static/uploads/{unique_filename}"
                        new_image_paths.append(relative_path)
            
            # 合并现有图片和新上传的图片
            # 注意：如果前端传递了existing_images，则使用前端提供的现有图片列表
            # 否则保留原有的图片
            if existing_images:
                # 过滤出真正的服务器路径
                server_paths = [path for path in existing_images if path.startswith('/static/')]
                item.images = server_paths + new_image_paths
            else:
                # 如果没有提供existing_images，则将新图片添加到现有图片中
                item.images = item.images + new_image_paths
        
        else:
            return jsonify({"msg": "Unsupported media type"}), 415
        
        # 更新时间戳
        item.update_timestamp()
        item.save()
        
        return jsonify({
            "msg": "Item updated successfully",
            "item_id": str(item.id),
            "images": item.images
        }), 200
    except ValidationError as e:
        return jsonify({"msg": "Validation error", "errors": str(e)}), 400
    except Exception as e:
        print(f"Error updating item: {e}")
        return jsonify({"msg": "An internal error occurred"}), 500

@item_bp.route('/<item_id>', methods=['DELETE'])
@jwt_required()
def delete_item(item_id):
    """删除商品"""
    current_user_id = get_jwt_identity()
    
    try:
        item = Item.objects(id=item_id).first()
        
        if not item:
            return jsonify({"msg": "Item not found"}), 404
        
        # 检查是否是商品卖家
        if str(item.seller.id) != current_user_id:
            return jsonify({"msg": "Unauthorized: You are not the seller of this item"}), 403
        
        # 删除商品
        item.delete()
        
        return jsonify({"msg": "Item deleted successfully"}), 200
    except Exception as e:
        print(f"Error deleting item: {e}")
        return jsonify({"msg": "An internal error occurred"}), 500

@item_bp.route('/user', methods=['GET'])
@jwt_required()
def get_user_items():
    """获取当前登录用户发布的所有商品"""
    current_user_id = get_jwt_identity()
    
    try:
        # 查询当前用户发布的所有商品
        items = Item.objects(seller=current_user_id)
        
        # 获取总数
        total_count = items.count()
        
        # 格式化结果
        result = []
        for item in items:
            seller_data = {
                "id": str(item.seller.id),
                "username": item.seller.username
            }
            
            result.append({
                "id": str(item.id),
                "title": item.title,
                "description": item.description,
                "price": item.price,
                "category": item.category,
                "images": item.images,
                "seller": seller_data,
                "created_at": item.created_at.isoformat(),
                "updated_at": item.updated_at.isoformat(),
                "status": item.status,
                "views": item.views
            })
        
        # 返回结果
        return jsonify({
            "total": total_count,
            "items": result
        }), 200
    except Exception as e:
        print(f"Error fetching user items: {e}")
        return jsonify({"msg": "An internal error occurred"}), 500 