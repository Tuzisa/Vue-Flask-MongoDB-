<template>
  <div class="profile-container">
    <div class="profile-header">
      <el-card class="user-info-card">
        <div class="user-info">
          <el-avatar :size="80" :src="avatarUrl" @error="handleAvatarError">
            <el-icon><User /></el-icon>
          </el-avatar>
          <div class="user-details">
            <h2>{{ userInfo.username || '用户名' }}</h2>
            <p class="join-time">加入时间：{{ formatDate(userInfo.joinedAt) }}</p>
            <p class="user-email" v-if="userInfo.email">{{ userInfo.email }}</p>
          </div>
          <div class="user-actions">
            <el-button type="primary" size="small" @click="goToSettings">
              <el-icon><Setting /></el-icon> 个人设置
            </el-button>
          </div>
        </div>
        <div class="user-stats">
          <div class="stat-item">
            <div class="stat-value">{{ userStats.itemsCount || 0 }}</div>
            <div class="stat-label">发布商品</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ userStats.totalViews || 0 }}</div>
            <div class="stat-label">总浏览量</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ userStats.favoritesCount || 0 }}</div>
            <div class="stat-label">收藏数</div>
          </div>
        </div>
      </el-card>
    </div>

    <div class="profile-content">
      <el-tabs v-model="activeTab" class="profile-tabs">
        <el-tab-pane label="我发布的商品" name="published">
          <div v-if="loading.published" class="loading-placeholder">
            <el-skeleton :rows="3" animated />
          </div>
          <div v-else-if="publishedItems.length === 0" class="empty-state">
            <el-empty description="您还没有发布过商品">
              <el-button type="primary" @click="$router.push('/publish')">去发布商品</el-button>
            </el-empty>
          </div>
          <div v-else class="items-grid">
            <div v-for="item in publishedItems" :key="item.id" class="item-card">
              <div class="item-image" @click="viewItem(item.id)">
                <img :src="getImageUrl(item)" :alt="item.title">
                <div class="item-status" :class="item.status">{{ getStatusText(item.status) }}</div>
              </div>
              <div class="item-info">
                <div class="item-title" @click="viewItem(item.id)">{{ item.title }}</div>
                <div class="item-price">¥ {{ item.price.toFixed(2) }}</div>
                <div class="item-meta">
                  <span class="item-date">{{ formatDate(item.createdAt) }}</span>
                  <span class="item-views"><el-icon><View /></el-icon> {{ item.views }}</span>
                </div>
                <div class="item-actions">
                  <el-button type="primary" size="small" plain @click="editItem(item.id)">编辑</el-button>
                  <el-dropdown trigger="click" @command="handleCommand">
                    <el-button size="small" plain>
                      更多<el-icon class="el-icon--right"><arrow-down /></el-icon>
                    </el-button>
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item :command="{ action: 'changeStatus', id: item.id, status: 'available' }" 
                          :disabled="item.status === 'available'">标记为在售</el-dropdown-item>
                        <el-dropdown-item :command="{ action: 'changeStatus', id: item.id, status: 'reserved' }"
                          :disabled="item.status === 'reserved'">标记为已预订</el-dropdown-item>
                        <el-dropdown-item :command="{ action: 'changeStatus', id: item.id, status: 'sold' }"
                          :disabled="item.status === 'sold'">标记为已售出</el-dropdown-item>
                        <el-dropdown-item divided :command="{ action: 'delete', id: item.id }" class="danger">删除</el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="我收藏的商品" name="favorites">
          <div v-if="loading.favorites" class="loading-placeholder">
            <el-skeleton :rows="3" animated />
          </div>
          <div v-else-if="favoriteItems.length === 0" class="empty-state">
            <el-empty description="您还没有收藏任何商品">
              <el-button type="primary" @click="$router.push('/items')">去浏览商品</el-button>
            </el-empty>
          </div>
          <div v-else class="items-grid">
            <div v-for="item in favoriteItems" :key="item.id" class="item-card">
              <div class="item-image" @click="viewItem(item.id)">
                <img :src="getImageUrl(item)" :alt="item.title">
                <div v-if="item.status !== 'available'" class="item-status" :class="item.status">
                  {{ getStatusText(item.status) }}
                </div>
              </div>
              <div class="item-info">
                <div class="item-title" @click="viewItem(item.id)">{{ item.title }}</div>
                <div class="item-price">¥ {{ item.price.toFixed(2) }}</div>
                <div class="item-meta">
                  <span class="item-seller">{{ item.seller.username }}</span>
                  <span class="item-date">{{ formatDate(item.createdAt) }}</span>
                </div>
                <div class="item-actions">
                  <el-button type="danger" size="small" plain @click="removeFavorite(item.id)">取消收藏</el-button>
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="浏览历史" name="history">
          <div v-if="loading.history" class="loading-placeholder">
            <el-skeleton :rows="3" animated />
          </div>
          <div v-else-if="browseHistory.length === 0" class="empty-state">
            <el-empty description="暂无浏览历史">
              <el-button type="primary" @click="$router.push('/items')">去浏览商品</el-button>
            </el-empty>
          </div>
          <div v-else class="history-list">
            <div v-for="(item, index) in browseHistory" :key="index" class="history-item" @click="viewItem(item.id)">
              <div class="history-image">
                <img :src="getImageUrl(item)" :alt="item.title" @error="handleImageError($event)">
              </div>
              <div class="history-info">
                <div class="history-title">{{ item.title }}</div>
                <div class="history-price">¥ {{ item.price ? item.price.toFixed(2) : '0.00' }}</div>
                <div class="history-meta">
                  <span>浏览时间: {{ formatDate(item.viewedAt) }}</span>
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useItemStore } from '@/stores/item';
import { useFavoriteStore } from '@/stores/favorite';
import { ElMessage, ElMessageBox } from 'element-plus';
import { View, ArrowDown, User, Setting } from '@element-plus/icons-vue';
import { itemApi, userApi, analyticsApi, itemHelpers } from '@/services/api';

const router = useRouter();
const authStore = useAuthStore();
const itemStore = useItemStore();
const favoriteStore = useFavoriteStore();

// 状态
const activeTab = ref('published');
const publishedItems = ref([]);
const favoriteItems = ref([]);
const browseHistory = ref([]);
const userInfo = reactive({
  username: '',
  joinedAt: '',
  email: '',
  avatar: null
});
const userStats = reactive({
  itemsCount: 0,
  totalViews: 0,
  favoritesCount: 0,
});
const loading = reactive({
  published: true,
  favorites: true,
  history: true,
  stats: true,
});

// 当前用户ID
const userId = computed(() => authStore.userId);

// 初始化加载数据
onMounted(async () => {
  if (!authStore.isAuthenticated) {
    ElMessage.warning('请先登录');
    router.push('/login');
    return;
  }

  // 刷新用户信息
  await authStore.refreshUserInfo();

  // 更新本地用户信息
  userInfo.username = authStore.username;
  userInfo.joinedAt = authStore.user?.created_at || new Date().toISOString();
  userInfo.email = authStore.user?.email || '';
  userInfo.avatar = authStore.user?.avatar || null;

  // 强制刷新所有数据
  await Promise.all([
    loadUserStats(),
    loadPublishedItems(),
    favoriteStore.loadFavorites()
  ]);

  // 加载当前激活的标签页数据
  loadTabData(activeTab.value);
});

// 监听标签页变化
watch(activeTab, (newTab) => {
  console.log('切换到标签页:', newTab);
  loadTabData(newTab);
});

// 加载发布的商品
const loadPublishedItems = async () => {
  if (!authStore.isAuthenticated) return;
  loading.published = true;

  try {
    console.log('当前用户ID:', authStore.userId);
    console.log('当前用户名:', authStore.username);
    
    // 使用简化的API加载用户商品，不传递userId参数
    const result = await itemHelpers.loadUserItems();
    publishedItems.value = result.items || [];
    console.log('用户发布的商品:', publishedItems.value);
    
    // 更新发布商品数量
    userStats.itemsCount = publishedItems.value.length;
  } catch (error) {
    console.error('加载发布的商品失败', error);
    ElMessage.error('加载发布的商品失败');
    publishedItems.value = [];
    // 如果加载失败，设置商品数量为0
    userStats.itemsCount = 0;
  } finally {
    loading.published = false;
  }
};

// 加载收藏的商品
const loadFavoriteItems = async () => {
  if (!authStore.isAuthenticated) return;
  loading.favorites = true;
  favoriteItems.value = [];

  try {
    // 加载收藏列表
    await favoriteStore.loadFavorites();
    console.log('收藏列表:', favoriteStore.favorites);
    
    // 获取收藏商品的详细信息
    const favoriteIds = favoriteStore.favoriteItemIds;
    console.log('收藏商品IDs:', favoriteIds);
    
    if (favoriteIds.length === 0) {
      favoriteItems.value = [];
      return;
    }

    // 方法1：使用单独的API请求获取每个收藏商品的详细信息
    const itemPromises = favoriteIds.map(id => 
      itemApi.getItem(id)
        .then(response => response.data)
        .catch(error => {
          console.error(`获取商品 ${id} 详情失败:`, error);
          return null;
        })
    );
    
    const itemResults = await Promise.all(itemPromises);
    favoriteItems.value = itemResults.filter(item => item !== null);
    console.log('收藏商品详情:', favoriteItems.value);
  } catch (error) {
    console.error('加载收藏的商品失败', error);
    ElMessage.error('加载收藏的商品失败');
    favoriteItems.value = [];
  } finally {
    loading.favorites = false;
  }
};

// 加载浏览历史
const loadBrowseHistory = async () => {
  if (!authStore.isAuthenticated) return;
  loading.history = true;
  browseHistory.value = [];

  try {
    console.log('开始加载浏览历史...');
    const response = await userApi.getBrowseHistory();
    console.log('浏览历史响应:', response);
    
    if (response && response.history && Array.isArray(response.history)) {
      browseHistory.value = response.history;
      console.log('浏览历史加载成功, 数量:', browseHistory.value.length);
      
      // 确保每个历史记录项都有有效的图片路径
      browseHistory.value.forEach(item => {
        if (!item.images || item.images.length === 0) {
          item.images = ['/placeholder.jpg'];
        }
      });
    } else {
      console.warn('浏览历史数据格式不正确:', response);
      browseHistory.value = [];
    }
  } catch (error) {
    console.error('加载浏览历史失败', error);
    ElMessage.error('加载浏览历史失败');
    browseHistory.value = [];
  } finally {
    loading.history = false;
  }
};

// 加载用户统计信息
const loadUserStats = async () => {
  if (!authStore.isAuthenticated) return;
  loading.stats = true;

  try {
    const response = await analyticsApi.getUserStats();
    
    userStats.itemsCount = response.items_count || 0;
    userStats.totalViews = response.total_views || 0;
    
    // 使用后端返回的收藏数量
    userStats.favoritesCount = response.favorites_count || 0;
    
    // 确保收藏列表是最新的
    await favoriteStore.loadFavorites();
  } catch (error) {
    console.error('加载用户统计信息失败', error);
  } finally {
    loading.stats = false;
  }
};

// 查看商品详情
const viewItem = (itemId) => {
  router.push({ name: 'ItemDetail', params: { id: itemId } });
};

// 编辑商品
const editItem = (itemId) => {
  router.push({ name: 'EditItem', params: { id: itemId } });
};

// 取消收藏
const removeFavorite = async (itemId) => {
  try {
    await favoriteStore.removeFavorite(itemId);
    ElMessage.success('已取消收藏');
    
    // 从收藏列表中移除
    favoriteItems.value = favoriteItems.value.filter(item => item.id !== itemId);
    
    // 更新收藏数量
    userStats.favoritesCount = favoriteStore.favorites.length;
  } catch (error) {
    console.error('取消收藏失败', error);
    ElMessage.error('取消收藏失败');
  }
};

// 处理下拉菜单命令
const handleCommand = ({ action, id, status }) => {
  if (action === 'changeStatus') {
    changeItemStatus(id, status);
  } else if (action === 'delete') {
    confirmDeleteItem(id);
  }
};

// 改变商品状态
const changeItemStatus = async (itemId, status) => {
  try {
    await itemStore.updateItem(itemId, { status });
    ElMessage.success('状态更新成功');
    
    // 更新本地状态
    const item = publishedItems.value.find(i => i.id === itemId);
    if (item) {
      item.status = status;
    }
  } catch (error) {
    console.error('更新商品状态失败', error);
    ElMessage.error('更新商品状态失败');
  }
};

// 确认删除商品
const confirmDeleteItem = (itemId) => {
  ElMessageBox.confirm('确定要删除该商品吗？此操作不可逆', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await itemStore.deleteItem(itemId);
      ElMessage.success('商品已删除');
      
      // 从列表中移除
      publishedItems.value = publishedItems.value.filter(item => item.id !== itemId);
      
      // 更新发布商品数量 - 使用实际长度而不是减1
      userStats.itemsCount = publishedItems.value.length;
    } catch (error) {
      console.error('删除商品失败', error);
      ElMessage.error('删除商品失败');
    }
  }).catch(() => {});
};

// 获取商品状态文本
const getStatusText = (status) => {
  const statusMap = {
    'available': '在售',
    'reserved': '已预订',
    'sold': '已售出'
  };
  return statusMap[status] || status;
};

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '未知';
  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return '未知';
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  } catch (error) {
    console.error('日期格式化错误:', error);
    return '未知';
  }
};

// 获取图片URL
const getImageUrl = (item) => {
  // 如果没有item或者没有images属性，返回默认图片
  if (!item || !item.images) {
    console.log('项目没有图片，使用默认图片');
    return '/placeholder.jpg';
  }
  
  // 如果是浏览历史中的item，可能有不同的图片格式
  if (item.images && Array.isArray(item.images) && item.images.length > 0) {
    const firstImage = item.images[0];
    console.log('处理图片URL:', firstImage);
    
    // 处理不同格式的图片路径
    if (typeof firstImage === 'string') {
      // 如果是服务器路径，添加基础URL
      if (firstImage.startsWith('/static')) {
        const baseUrl = import.meta.env.VITE_API_BASE_URL || '';
        return `${baseUrl}${firstImage}`;
      }
      return firstImage;
    }
  }
  
  // 使用辅助函数处理其他情况
  return itemHelpers.getImageUrl(item);
};

// 监听标签页变化
const loadTabData = (tabName) => {
  // 每次切换标签页时重新加载用户统计信息
  loadUserStats();
  
  switch (tabName) {
    case 'published':
      loadPublishedItems();
      break;
    case 'favorites':
      loadFavoriteItems();
      break;
    case 'history':
      loadBrowseHistory();
      break;
  }
};

// 处理图片加载错误
const handleImageError = (event) => {
  console.log('图片加载失败，使用默认图片');
  event.target.src = '/placeholder.jpg';
};

// 获取头像URL
const avatarUrl = computed(() => {
  const baseUrl = import.meta.env.VITE_API_BASE_URL || '';
  if (userInfo.avatar) {
    return userInfo.avatar.startsWith('/static') 
      ? `${baseUrl}${userInfo.avatar}` 
      : userInfo.avatar;
  }
  return `${baseUrl}/static/avatars/default_avatar.jpg`;
});

// 处理头像加载错误
const handleAvatarError = (event) => {
  const baseUrl = import.meta.env.VITE_API_BASE_URL || '';
  event.target.src = `${baseUrl}/static/avatars/default_avatar.jpg`;
};

// 跳转到设置页面
const goToSettings = () => {
  router.push('/settings');
};
</script>

<style scoped>
.profile-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.profile-header {
  margin-bottom: 20px;
}

.user-info-card {
  border-radius: 8px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
}

.user-details {
  flex: 1;
}

.user-details h2 {
  margin: 0 0 10px 0;
  font-size: 24px;
}

.join-time {
  color: #909399;
  margin: 0;
}

.user-email {
  color: #606266;
  margin: 5px 0 0 0;
  font-size: 14px;
}

.user-actions {
  display: flex;
  gap: 10px;
}

.user-stats {
  display: flex;
  justify-content: space-around;
  text-align: center;
  margin-top: 10px;
}

.stat-item {
  padding: 10px 20px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

.profile-content {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  padding: 20px;
}

.loading-placeholder {
  padding: 20px;
}

.empty-state {
  padding: 40px 0;
  text-align: center;
}

.items-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.item-card {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  background-color: #fff;
}

.item-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.item-image {
  height: 200px;
  overflow: hidden;
  position: relative;
  cursor: pointer;
}

.item-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.item-status {
  position: absolute;
  top: 10px;
  right: 10px;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
  color: #fff;
  background-color: #67c23a;
}

.item-status.sold {
  background-color: #909399;
}

.item-status.reserved {
  background-color: #e6a23c;
}

.item-info {
  padding: 15px;
}

.item-title {
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 10px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  cursor: pointer;
}

.item-price {
  font-size: 18px;
  font-weight: 600;
  color: #ff4d4f;
  margin-bottom: 10px;
}

.item-meta {
  display: flex;
  justify-content: space-between;
  color: #909399;
  font-size: 12px;
  margin-bottom: 15px;
}

.item-views {
  display: flex;
  align-items: center;
  gap: 5px;
}

.item-actions {
  display: flex;
  justify-content: space-between;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-top: 20px;
}

.history-item {
  display: flex;
  border-radius: 8px;
  background-color: #fff;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.history-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.history-image {
  width: 120px;
  height: 90px;
  overflow: hidden;
}

.history-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.history-info {
  flex: 1;
  padding: 10px 15px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.history-title {
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 5px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.history-price {
  font-size: 16px;
  font-weight: 600;
  color: #ff4d4f;
}

.history-meta {
  font-size: 12px;
  color: #909399;
}

.danger {
  color: #f56c6c;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .items-grid {
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  }
  
  .user-info {
    flex-direction: column;
    text-align: center;
  }
  
  .user-stats {
    flex-wrap: wrap;
  }
}
</style> 