<template>
  <div class="item-detail-container">
    <div class="item-detail-box">
      <!-- 返回按钮 -->
      <div class="back-button">
        <el-button @click="$router.go(-1)" circle plain>
          <el-icon><ArrowLeft /></el-icon>
        </el-button>
      </div>

      <div class="item-detail-content">
        <!-- 左侧图片区域 -->
        <div class="item-images">
          <el-carousel v-if="item && item.images && item.images.length > 0" :interval="4000" type="card" height="400px">
            <el-carousel-item v-for="(image, index) in item.images" :key="index">
              <img :src="image" :alt="item.title + ' 图片 ' + (index + 1)" class="carousel-image">
            </el-carousel-item>
          </el-carousel>
          <div v-else class="no-image">
            <el-icon><Picture /></el-icon>
            <span>暂无图片</span>
          </div>
        </div>

        <!-- 右侧信息区域 -->
        <div class="item-info">
          <div class="item-header">
            <h1 class="item-title">{{ item?.title || '加载中...' }}</h1>
            <div class="item-price">¥ {{ item?.price?.toFixed(2) || '0.00' }}</div>
          </div>

          <div class="item-meta">
            <div class="meta-item">
              <el-icon><Calendar /></el-icon>
              <span>发布时间：{{ formatDate(item?.created_at) }}</span>
            </div>
            <div class="meta-item">
              <el-icon><View /></el-icon>
              <span>浏览次数：{{ item?.views || 0 }}</span>
            </div>
            <div class="meta-item">
              <el-icon><Collection /></el-icon>
              <span>分类：{{ getCategoryName(item?.category) }}</span>
            </div>
          </div>

          <div class="item-actions">
            <el-button 
              :type="isFavorited ? 'warning' : 'default'" 
              @click="toggleFavorite"
              class="action-button"
              :class="{ 'favorited': isFavorited }"
            >
              <template #icon>
                <el-icon :size="20"><Star /></el-icon>
              </template>
              {{ isFavorited ? '取消收藏' : '收藏' }}
            </el-button>
            <el-button 
              type="success" 
              @click="goToPurchasePage" 
              size="large"
              class="buy-now-btn action-button"
            >
              <template #icon>
                <el-icon :size="20"><ShoppingCart /></el-icon>
              </template>
              立即购买
            </el-button>
          </div>

          <div class="seller-info">
            <div class="seller-avatar">
              <el-avatar :size="50" :src="getUserAvatar(item?.seller)" icon="User"></el-avatar>
            </div>
            <div class="seller-details">
              <div class="seller-name">{{ item?.seller?.username || '未知用户' }}</div>
              <div class="seller-joined">加入时间：{{ formatDate(item?.seller?.created_at) }}</div>
            </div>
          </div>

          <el-divider>商品详情</el-divider>

          <div class="item-description">
            <p>{{ item?.description || '暂无描述' }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 评论区域 -->
    <CommentSection :product-id="route.params.id" />

    <!-- 相关推荐 -->
    <div class="related-items">
      <h2>相关推荐</h2>
      <div class="related-items-grid">
        <div v-for="(relatedItem, index) in relatedItems" :key="index" class="related-item-card" @click="goToItem(relatedItem.id)">
          <div class="related-item-image">
            <img :src="relatedItem.images[0] || 'default-placeholder.jpg'" :alt="relatedItem.title">
          </div>
          <div class="related-item-info">
            <div class="related-item-title">{{ relatedItem.title }}</div>
            <div class="related-item-price">¥ {{ relatedItem.price.toFixed(2) }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useItemStore } from '@/stores/item';
import { useFavoriteStore } from '@/stores/favorite';
import { useAuthStore } from '@/stores/auth';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Picture, Calendar, View, Collection, StarFilled, Star, ArrowLeft, ShoppingCart } from '@element-plus/icons-vue';
import { userApi } from '@/services/api';
import CommentSection from '@/components/CommentSection.vue';

const route = useRoute();
const router = useRouter();
const itemStore = useItemStore();
const favoriteStore = useFavoriteStore();
const authStore = useAuthStore();

const item = ref(null);
const relatedItems = ref([]);
const loading = ref(true);

// 封装加载商品数据的逻辑为一个函数
const loadItemDetails = async (itemId) => {
  if (!itemId) {
    ElMessage.error('商品ID不存在');
    router.push('/items');
    return;
  }

  try {
    loading.value = true;
    item.value = await itemStore.fetchItemById(itemId);
    
    // 加载相关推荐，确保在 item.value 更新后再调用
    if (item.value) {
      loadRelatedItems();
    }
    
    // 如果已登录，加载收藏信息
    if (authStore.isAuthenticated) {
      await favoriteStore.loadFavorites();
      console.log('当前商品是否已收藏:', favoriteStore.isFavorited(itemId));
      
      // 记录浏览历史
      try {
        console.log('记录浏览历史, 商品ID:', itemId);
        await userApi.addBrowseHistory(itemId);
      } catch (error) {
        console.error('记录浏览历史失败', error);
      }
    }
  } catch (error) {
    console.error('获取商品详情失败', error);
    ElMessage.error('获取商品详情失败');
    item.value = null; // 获取失败时清空，避免显示旧数据
  } finally {
    loading.value = false;
  }
};

// 检查是否收藏
const isFavorited = computed(() => {
  if (!item.value || !authStore.isAuthenticated) return false;
  return favoriteStore.isFavorited(item.value.id);
});

// 加载商品详情
onMounted(() => {
  loadItemDetails(route.params.id);
});

// 监听路由参数id的变化，当它变化时重新加载商品数据
watch(() => route.params.id, (newId, oldId) => {
  if (newId && newId !== oldId) {
    console.log(`路由参数 id 从 ${oldId} 变为 ${newId}，重新加载商品详情。`);
    // 清理可能存在的旧状态，例如相关推荐
    relatedItems.value = [];
    // 滚动到页面顶部是一个好习惯
    window.scrollTo(0, 0);
    loadItemDetails(newId);
  }
});

// 加载相关推荐商品
const loadRelatedItems = async () => {
  if (!item.value) return;

  // 保存原始的 store 过滤和排序状态的 *values*
  const originalCategoryFilterValue = itemStore.categoryFilter;
  const originalSortByValue = itemStore.sortBy;
  const originalSortOrderValue = itemStore.sortOrder;

  try {
    // 设置获取相关推荐的过滤和排序条件
    itemStore.setCategoryFilter(item.value.category);
    itemStore.setSortOptions('views', 'desc'); // 按浏览量降序排序

    // 根据分类获取相关商品，fetchItems内部会使用store的过滤和排序状态
    const rawAxiosResponse = await itemStore.fetchItems(1, false); // 获取第一页，这是原始Axios响应
    console.log('[loadRelatedItems] Raw Axios Response from store:', rawAxiosResponse);
    
    // 实际的商品数据在 rawAxiosResponse.data.items
    if (rawAxiosResponse && rawAxiosResponse.data && rawAxiosResponse.data.items) {
      const itemsFromApi = rawAxiosResponse.data.items;
      console.log('[loadRelatedItems] Items from API (response.data.items):', JSON.parse(JSON.stringify(itemsFromApi)));
      
      // 从结果中排除当前商品，并取前4个
      const filteredItems = itemsFromApi
        .filter(i => {
          const isNotCurrentItem = i.id !== item.value.id;
          console.log(`[loadRelatedItems] Filtering item: ${i.title} (ID: ${i.id}), Is not current: ${isNotCurrentItem}, Views: ${i.views}`);
          return isNotCurrentItem;
        });
      console.log('[loadRelatedItems] Items after filtering current item:', JSON.parse(JSON.stringify(filteredItems)));
      
      relatedItems.value = filteredItems.slice(0, 4);
      console.log('[loadRelatedItems] Final relatedItems (up to 4):', JSON.parse(JSON.stringify(relatedItems.value)));
    } else {
      console.log('[loadRelatedItems] No items found in API response (expected in response.data.items) or response format incorrect.');
      relatedItems.value = []; // 确保在没有有效数据时清空
    }
  } catch (error) {
    console.error('加载相关商品失败', error);
    relatedItems.value = []; // 出错时清空，避免显示旧数据
  } finally {
    // 恢复原始的 store 过滤和排序状态的 *values*
    itemStore.setCategoryFilter(originalCategoryFilterValue);
    itemStore.setSortOptions(originalSortByValue, originalSortOrderValue);
  }
};

// 收藏/取消收藏
const toggleFavorite = async () => {
  if (!authStore.isAuthenticated) {
    ElMessageBox.confirm('请先登录后再收藏商品', '提示', {
      confirmButtonText: '去登录',
      cancelButtonText: '取消',
      type: 'warning'
    }).then(() => {
      router.push('/login');
    }).catch(() => {});
    return;
  }

  try {
    if (isFavorited.value) {
      await favoriteStore.removeFavorite(item.value.id);
      ElMessage.success('已取消收藏');
    } else {
      await favoriteStore.addFavorite(item.value.id);
      ElMessage.success('收藏成功');
    }
    
    // 强制重新加载收藏状态
    await favoriteStore.loadFavorites();
  } catch (error) {
    console.error('收藏操作失败', error);
    ElMessage.error('操作失败，请重试');
  }
};

// 跳转到模拟购买页面
const goToPurchasePage = () => {
  if (!authStore.isAuthenticated) {
    ElMessageBox.confirm('请先登录后再购买商品', '提示', {
      confirmButtonText: '去登录',
      cancelButtonText: '取消',
      type: 'warning'
    }).then(() => {
      router.push('/login');
    }).catch(() => {});
    return;
  }
  if (!item.value) return;
  router.push({ name: 'PurchasePage', params: { itemId: item.value.id } });
};

// 跳转到商品详情
const goToItem = (itemId) => {
  router.push({ name: 'ItemDetail', params: { id: itemId } });
};

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '未知';
  const date = new Date(dateString);
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
};

// 获取分类名称
const getCategoryName = (category) => {
  const categoryMap = {
    'electronics': '电子产品',
    'clothing': '服装',
    'books': '图书',
    'furniture': '家具',
    'other': '其他'
  };
  return categoryMap[category] || category || '未分类';
};

// 获取用户头像URL
const getUserAvatar = (user) => {
  if (!user) return '/assets/default-avatar.png';
  
  // 如果用户有头像路径
  if (user.avatar) {
    // 服务器基础URL
    const baseUrl = import.meta.env.VITE_API_BASE_URL || '';
    
    // 如果是以/static开头的服务器路径
    if (user.avatar.startsWith('/static')) {
      return `${baseUrl}${user.avatar}`;
    }
    // 如果是完整URL或Base64
    if (user.avatar.startsWith('http') || user.avatar.startsWith('data:')) {
      return user.avatar;
    }
    return user.avatar;
  }
  
  // 返回默认头像 - 尝试多个可能的路径
  const possiblePaths = [
    '/pic/default-avatar.png',
    '/assets/default-avatar.png',
    '/images/default-avatar.png',
    'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png' // Element Plus 默认头像
  ];
  
  // 使用一个公共的默认头像URL作为最后的后备
  return possiblePaths[3];
};
</script>

<style scoped>
.item-detail-container {
  padding: 20px 0;
}

.item-detail-box {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  padding: 20px;
  position: relative;
}

.back-button {
  position: absolute;
  top: 20px;
  left: 20px;
  z-index: 10;
}

.item-detail-content {
  display: flex;
  flex-direction: row;
  gap: 30px;
  margin-top: 40px;
}

.item-images {
  flex: 1;
  max-width: 50%;
  overflow: hidden;
}

.el-carousel__item {
  overflow: hidden;
  border-radius: 4px;
  background-color: #f5f7fa;
}

.carousel-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  border-radius: 4px;
  background-color: #f5f7fa;
  transition: transform 0.3s ease;
  cursor: zoom-in;
}

.carousel-image:hover {
  transform: scale(1.2);
}

.no-image {
  width: 100%;
  height: 400px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background-color: #f5f7fa;
  border-radius: 4px;
  color: #909399;
}

.no-image i {
  font-size: 48px;
  margin-bottom: 10px;
}

.item-info {
  flex: 1;
}

.item-header {
  margin-bottom: 20px;
}

.item-title {
  font-size: 24px;
  font-weight: 600;
  margin: 0 0 10px 0;
}

.item-price {
  font-size: 28px;
  font-weight: 700;
  color: #ff4d4f;
}

.item-meta {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 20px;
}

.meta-item {
  display: flex;
  align-items: center;
  color: #606266;
}

.meta-item i {
  margin-right: 8px;
}

.item-actions {
  display: flex;
  gap: 15px;
  margin-bottom: 30px;
}

.favorited {
  background-color: #ff9900 !important;
  color: #fff !important;
  border-color: #ff9900 !important;
}

.favorited:hover {
  background-color: #e68a00 !important;
  border-color: #e68a00 !important;
}

.seller-info {
  display: flex;
  align-items: center;
  gap: 15px;
  background-color: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.seller-details {
  display: flex;
  flex-direction: column;
}

.seller-name {
  font-size: 16px;
  font-weight: 600;
}

.seller-joined {
  font-size: 14px;
  color: #909399;
}

.item-description {
  line-height: 1.6;
  color: #606266;
  white-space: pre-wrap;
}

.related-items {
  margin-top: 40px;
}

.related-items h2 {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 20px;
}

.related-items-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 20px;
}

.related-item-card {
  background-color: #fff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  cursor: pointer;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.related-item-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.related-item-image {
  height: 150px;
  overflow: hidden;
}

.related-item-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.related-item-info {
  padding: 12px;
}

.related-item-title {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.related-item-price {
  font-size: 16px;
  font-weight: 600;
  color: #ff4d4f;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .item-detail-content {
    flex-direction: column;
  }
  
  .item-images {
    max-width: 100%;
  }
}

.action-button {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 12px 20px;
  font-weight: 500;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.action-button .el-icon {
  margin-right: 5px;
}

.buy-now-btn {
  flex-grow: 1;
  font-size: 16px;
}

.buy-now-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
</style> 