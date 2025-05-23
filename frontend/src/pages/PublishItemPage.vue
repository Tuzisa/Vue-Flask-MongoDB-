<template>
  <div class="publish-container">
    <h1>{{ isEditMode ? '编辑商品' : '发布二手商品' }}</h1>
    <form @submit.prevent="submitItem" class="publish-form">
      <div class="form-group">
        <label for="title">商品标题</label>
        <input 
          type="text" 
          id="title" 
          v-model="item.title" 
          required 
          placeholder="请输入商品标题（2-30字）"
          maxlength="30"
        />
      </div>

      <div class="form-group">
        <label for="price">价格 (元)</label>
        <input 
          type="number" 
          id="price" 
          v-model="item.price" 
          required 
          min="0"
          placeholder="请输入价格"
        />
      </div>

      <div class="form-group">
        <label for="category">分类</label>
        <select id="category" v-model="item.category" required>
          <option value="">请选择分类</option>
          <option value="electronics">电子产品</option>
          <option value="clothing">服装</option>
          <option value="books">图书</option>
          <option value="furniture">家具</option>
          <option value="other">其他</option>
        </select>
      </div>

      <div class="form-group">
        <label for="description">描述</label>
        <textarea 
          id="description" 
          v-model="item.description" 
          required 
          placeholder="请详细描述您的商品，如新旧程度、配件情况等"
          rows="5"
          maxlength="500"
        ></textarea>
        <div class="char-count">{{ item.description.length }}/500</div>
      </div>

      <div class="form-group">
        <label for="image">商品图片</label>
        <SimpleImageUploader 
          v-model="item.images" 
          :maxImages="5"
        />
      </div>

      <div class="form-actions">
        <button type="button" @click="$router.go(-1)" class="btn-cancel">取消</button>
        <button type="submit" class="btn-submit" :disabled="isSubmitting">
          {{ isSubmitting ? '发布中...' : '发布商品' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ElMessage } from 'element-plus';
import { useAuthStore } from '@/stores/auth';
import { ref, reactive, onMounted, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { itemApi, analyticsApi } from '@/services/api';
import SimpleImageUploader from '@/components/SimpleImageUploader.vue';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

// 判断是否是编辑模式
const isEditMode = computed(() => route.meta.isEdit);
const itemId = computed(() => route.params.id);

// 商品数据
const item = reactive({
  title: '',
  price: '',
  category: '',
  description: '',
  images: []
});

const isSubmitting = ref(false);
const isLoading = ref(false);

// 检查用户是否已登录并加载商品数据（如果是编辑模式）
onMounted(async () => {
  if (!authStore.isAuthenticated) {
    ElMessage.warning('请先登录后再操作');
    router.push('/login');
    return;
  }
  
  // 如果是编辑模式，加载商品数据
  if (isEditMode.value && itemId.value) {
    isLoading.value = true;
    try {
      const response = await itemApi.getItem(itemId.value);
      const itemData = response.data;
      
      // 填充表单数据
      item.title = itemData.title;
      item.price = itemData.price.toString();
      item.category = itemData.category;
      item.description = itemData.description;
      
      // 处理图片
      if (itemData.images && itemData.images.length > 0) {
        // 转换图片格式以适应SimpleImageUploader组件
        item.images = itemData.images.map((img, index) => {
          let imageUrl;
          // 如果图片是字符串路径
          if (typeof img === 'string') {
            imageUrl = img.startsWith('/') ? `${import.meta.env.VITE_API_BASE_URL}${img}` : img;
          }
          // 如果图片是对象
          else if (typeof img === 'object') {
            imageUrl = img.path ? 
              `${import.meta.env.VITE_API_BASE_URL}${img.path}` : 
              (img.url || '');
          }

          return {
            id: index,
            url: imageUrl,
            isExisting: true,
            name: `existing-image-${index}.jpg`
          };
        }).filter(img => img.url);
      }
    } catch (error) {
      console.error('加载商品数据失败:', error);
      ElMessage.error('无法加载商品数据，请重试');
      router.push('/profile');
    } finally {
      isLoading.value = false;
    }
  }
});

// 提交商品信息
const submitItem = async () => {
  // 验证表单
  if (!item.title || !item.price || !item.category || !item.description) {
    ElMessage.warning('请填写所有必填字段');
    return;
  }
  
  // 价格必须是有效数字
  if (isNaN(parseFloat(item.price)) || parseFloat(item.price) < 0) {
    ElMessage.warning('请输入有效的价格');
    return;
  }
  
  isSubmitting.value = true;
  
  try {
    // 准备商品数据和图片文件
    const formData = new FormData();
    formData.append('title', item.title);
    formData.append('price', parseFloat(item.price));
    formData.append('category', item.category);
    formData.append('description', item.description);
    formData.append('seller_id', authStore.userId);
    
    // 处理图片文件
    if (item.images && item.images.length > 0) {
      console.log('准备处理图片:', item.images);
      
      // 收集新上传的图片文件和已存在的图片
      const newImages = item.images.filter(image => image.file);
      const existingImages = item.images.filter(image => image.isExisting);
      
      // 如果是编辑模式，处理已有图片
      if (isEditMode.value) {
        // 只有当保留了一些原有图片时才添加 existing_images
        if (existingImages.length > 0) {
          const existingImagePaths = existingImages.map(image => {
            const url = image.url;
            // 如果URL包含完整的服务器地址，需要移除它
            const baseUrl = import.meta.env.VITE_API_BASE_URL;
            if (baseUrl && url.startsWith(baseUrl)) {
              return url.substring(baseUrl.length);
            }
            // 如果是相对路径，直接使用
            return url;
          });
          
          formData.append('existing_images', JSON.stringify(existingImagePaths));
        } else {
          // 如果没有保留任何原有图片，发送空数组表示清除所有原有图片
          formData.append('existing_images', JSON.stringify([]));
        }
      }
      
      // 添加新图片文件
      if (newImages.length > 0) {
        newImages.forEach((image, index) => {
          if (image.file) {
            formData.append('images', image.file);
          }
        });
      }
    } else {
      // 如果没有任何图片，在编辑模式下需要清除所有原有图片
      if (isEditMode.value) {
        formData.append('existing_images', JSON.stringify([]));
      }
    }
    
    let response;
    
    // 根据模式选择创建或更新操作
    if (isEditMode.value) {
      console.log('准备更新商品:', {
        id: itemId.value,
        title: item.title,
        price: parseFloat(item.price),
        category: item.category,
        imagesCount: (item.images || []).length
      });
      
      response = await itemApi.updateItem(itemId.value, formData);
      console.log('商品更新成功，响应:', response);
      ElMessage.success('商品更新成功！');
    } else {
      console.log('准备发布商品:', {
        title: item.title,
        price: parseFloat(item.price),
        category: item.category,
        imagesCount: (item.images || []).length
      });
      
      response = await itemApi.createItem(formData);
      console.log('商品发布成功，响应:', response);
      ElMessage.success('商品发布成功！');
      
      // 强制刷新用户统计数据
      try {
        await analyticsApi.getUserStats();
      } catch (error) {
        console.error('刷新用户统计数据失败:', error);
      }
    }
    
    // 成功后重定向到用户个人中心页面
    router.push({ name: 'UserProfile' });
  } catch (error) {
    console.error(`${isEditMode.value ? '更新' : '发布'}商品时发生错误:`, error);
    
    // 提供更详细的错误信息
    if (error.response) {
      console.error('响应状态:', error.response.status);
      console.error('响应数据:', error.response.data);
      
      const errorMsg = error.response.data?.message || 
                      error.response.data?.msg || 
                      error.response.data?.error ||
                      `${isEditMode.value ? '更新' : '发布'}失败，请重试`;
      
      ElMessage.error(errorMsg);
    } else if (error.message) {
      ElMessage.error(error.message);
    } else {
      ElMessage.error(`${isEditMode.value ? '更新' : '发布'}失败，服务器无响应`);
    }
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<style scoped>
.publish-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.publish-form {
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
}

input[type="text"],
input[type="number"],
select,
textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

.char-count {
  text-align: right;
  font-size: 0.8em;
  color: #666;
  margin-top: 5px;
}

.image-upload {
  border: 2px dashed #ddd;
  padding: 20px;
  border-radius: 4px;
  text-align: center;
  margin-top: 5px;
}

.upload-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 15px;
}

.preview-item {
  position: relative;
  width: 100px;
  height: 100px;
}

.preview-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 4px;
}

.remove-btn {
  position: absolute;
  top: -10px;
  right: -10px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background-color: rgba(255, 0, 0, 0.7);
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 30px;
}

.btn-cancel {
  padding: 10px 20px;
  background-color: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  color: #666;
}

.btn-submit {
  padding: 10px 20px;
  background-color: #67c23a;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}

.btn-submit:hover {
  background-color: #5daf34;
}

.btn-submit:disabled {
  background-color: #a3d48e;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .publish-form {
    padding: 15px;
  }
  
  .btn-cancel, .btn-submit {
    padding: 8px 15px;
    font-size: 14px;
  }
}
</style> 