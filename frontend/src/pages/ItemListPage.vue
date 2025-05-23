<template>
  <div class="item-list-container">
    <h1>二手商品列表</h1>
    
    <!-- 集成搜索组件 -->
    <item-search-box 
      :initial-filters="searchFilters" 
      @search="handleSearch"
    />

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <el-skeleton :rows="5" animated />
    </div>

    <!-- 商品列表 -->
    <div class="items-grid" v-else-if="displayItems.length > 0">
      <div class="item-card" v-for="item in displayItems" :key="item.id" @click="viewItemDetail(item.id)">
        <div class="item-image">
          <img :src="getItemImageUrl(item)" :alt="item.title">
          <div v-if="item.status !== 'available'" class="item-status" :class="item.status">
            {{ getStatusText(item.status) }}
          </div>
        </div>
        <div class="item-info">
          <h3 class="item-title">{{ item.title }}</h3>
          <p class="price">¥{{ item.price.toFixed(2) }}</p>
          <p class="description">{{ item.description }}</p>
          <div class="item-meta">
            <span class="category">{{ getCategoryName(item.category) }}</span>
            <span class="date">{{ formatDate(item.created_at) }}</span>
          </div>
          <div class="item-footer">
            <span class="seller">{{ item.seller?.username || '未知用户' }}</span>
            <span class="views"><el-icon><View /></el-icon> {{ item.views || 0 }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 空状态 -->
    <div class="empty-state" v-else>
      <el-empty description="暂无符合条件的商品" :image-size="200">
        <template #description>
          <p>没有找到符合条件的商品</p>
          <p v-if="hasSearchFilters" class="empty-hint">您可以尝试调整搜索条件</p>
        </template>
        <el-button v-if="hasSearchFilters" type="primary" @click="resetSearch">清除所有筛选</el-button>
      </el-empty>
    </div>

    <!-- 分页控件 -->
    <div class="pagination-container" v-if="totalPages > 1">
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="totalItems"
        layout="prev, pager, next, jumper"
        @current-change="handlePageChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { ElMessage } from 'element-plus';
import { View } from '@element-plus/icons-vue';
import ItemSearchBox from '@/components/ItemSearchBox.vue';
import { itemApi, itemHelpers } from '@/services/api';

const router = useRouter();
const route = useRoute();

// 状态
const items = ref([]);
const loading = ref(false);
const currentPage = ref(1);
const pageSize = ref(12);
const totalItems = ref(0);

// 搜索筛选条件
const searchFilters = reactive({
  keyword: '',
  category: '',
  minPrice: '',
  maxPrice: '',
  sort: 'newest'
});

// 从URL参数初始化搜索条件
const initFiltersFromQuery = () => {
  const query = route.query;
  if (query.keyword) searchFilters.keyword = query.keyword;
  if (query.category) searchFilters.category = query.category;
  if (query.minPrice) searchFilters.minPrice = query.minPrice;
  if (query.maxPrice) searchFilters.maxPrice = query.maxPrice;
  if (query.sort) searchFilters.sort = query.sort;
  if (query.page) currentPage.value = parseInt(query.page) || 1;
};

// 计算是否有搜索筛选条件
const hasSearchFilters = computed(() => {
  return searchFilters.keyword || 
         searchFilters.category || 
         searchFilters.minPrice || 
         searchFilters.maxPrice || 
         searchFilters.sort !== 'newest';
});

// 计算总页数
const totalPages = computed(() => {
  return Math.ceil(totalItems.value / pageSize.value);
});

// 计算当前显示的商品列表
const displayItems = computed(() => {
  return items.value;
});

// 监听路由变化
watch(() => route.query, () => {
  initFiltersFromQuery();
  fetchItems();
}, { deep: true });

// 组件挂载时初始化
onMounted(() => {
  initFiltersFromQuery();
  fetchItems();
});

// 处理搜索
const handleSearch = (filters) => {
  // 更新筛选条件
  Object.assign(searchFilters, filters);
  currentPage.value = 1; // 重置到第一页
  
  // 更新URL参数
  updateUrlQuery();
  
  // 获取商品数据
  fetchItems();
};

// 更新URL查询参数
const updateUrlQuery = () => {
  const query = {};
  
  if (searchFilters.keyword) query.keyword = searchFilters.keyword;
  if (searchFilters.category) query.category = searchFilters.category;
  if (searchFilters.minPrice) query.minPrice = searchFilters.minPrice;
  if (searchFilters.maxPrice) query.maxPrice = searchFilters.maxPrice;
  if (searchFilters.sort !== 'newest') query.sort = searchFilters.sort;
  if (currentPage.value > 1) query.page = currentPage.value;
  
  router.replace({ query });
};

// 处理分页变化
const handlePageChange = (page) => {
  currentPage.value = page;
  updateUrlQuery();
  fetchItems();
  
  // 滚动到顶部
  window.scrollTo({
    top: 0,
    behavior: 'smooth'
  });
};

// 重置搜索
const resetSearch = () => {
  searchFilters.keyword = '';
  searchFilters.category = '';
  searchFilters.minPrice = '';
  searchFilters.maxPrice = '';
  searchFilters.sort = 'newest';
  currentPage.value = 1;
  
  // 更新URL并获取数据
  updateUrlQuery();
  fetchItems();
};

// 查看商品详情
const viewItemDetail = (itemId) => {
  router.push({ name: 'ItemDetail', params: { id: itemId } });
};

// 获取商品数据
const fetchItems = async (retryCount = 0) => {
  loading.value = true;
  
  try {
    // 构建查询参数
    const params = {
      page: currentPage.value,
      limit: pageSize.value
    };
    
    if (searchFilters.keyword) params.keyword = searchFilters.keyword;
    if (searchFilters.category) params.category = searchFilters.category;
    
    // 确保价格筛选参数是数字类型
    if (searchFilters.minPrice !== undefined && searchFilters.minPrice !== '') {
      params.min_price = Number(searchFilters.minPrice);
    }
    if (searchFilters.maxPrice !== undefined && searchFilters.maxPrice !== '') {
      params.max_price = Number(searchFilters.maxPrice);
    }
    
    if (searchFilters.sort) params.sort = searchFilters.sort;
    
    // 使用带超时的请求
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10秒超时
    
    try {
      // 使用简化的API加载商品，添加signal参数用于超时控制
      console.log('发送商品查询参数:', params);
      const result = await itemHelpers.loadItems(params, controller.signal);
      console.log('商品列表数据:', result);
      
      // 设置商品列表和总数
      items.value = result.items || [];
      totalItems.value = result.total || 0;
      
      console.log('处理后的商品列表:', items.value);
      console.log('总商品数:', totalItems.value);
      
      // 清除超时
      clearTimeout(timeoutId);
    } catch (error) {
      // 清除超时
      clearTimeout(timeoutId);
      
      // 处理超时或中止
      if (error.name === 'AbortError') {
        console.error('请求超时或被中止');
        throw new Error('请求超时，请稍后重试');
      }
      
      throw error; // 重新抛出其他错误
    }
  } catch (error) {
    console.error('获取商品列表失败', error);
    
    // 处理网络连接错误
    if (
      error.code === 'ECONNABORTED' || 
      error.code === 'ECONNRESET' || 
      error.message?.includes('Network Error') ||
      error.message?.includes('timeout')
    ) {
      // 最多重试3次
      if (retryCount < 3) {
        console.log(`网络错误，正在进行第 ${retryCount + 1} 次重试...`);
        ElMessage.info(`加载失败，正在重试 (${retryCount + 1}/3)...`);
        
        // 递增重试次数并添加延迟
        setTimeout(() => {
          fetchItems(retryCount + 1);
        }, 1000 * (retryCount + 1)); // 递增延迟时间
        return;
      }
    }
    
    // 显示错误消息
    ElMessage.error(error.message || '获取商品列表失败，请重试');
    
    // 确保至少显示一些数据，即使是空的
    items.value = [];
    totalItems.value = 0;
  } finally {
    loading.value = false;
  }
};

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '';
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

// 获取商品状态文本
const getStatusText = (status) => {
  const statusMap = {
    'available': '在售',
    'reserved': '已预订',
    'sold': '已售出'
  };
  return statusMap[status] || status;
};

// 获取商品图片URL
const getItemImageUrl = (item) => {
  if (!item) return '';
  
  // 使用itemHelpers中的getImageUrl方法（如果存在）
  if (itemHelpers.getImageUrl) {
    return itemHelpers.getImageUrl(item);
  }
  
  // 后备逻辑 - 检查各种图片属性格式
  if (item.images && item.images.length > 0) {
    // 如果是字符串数组（URL数组）
    if (typeof item.images[0] === 'string') {
      return item.images[0];
    }
    
    // 如果是对象数组，尝试获取第一张图片的URL
    if (typeof item.images[0] === 'object') {
      // 支持不同的对象结构
      return item.images[0].url || item.images[0].path || item.images[0].src || 
             (item.images[0].data ? item.images[0].data : '');
    }
  }
  
  // 尝试获取单个图片属性
  return item.image_url || item.imageUrl || item.image || '/placeholder-image.png';
};
</script>

<style scoped>
.item-list-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.item-list-container h1 {
  font-size: 24px;
  margin-bottom: 20px;
  color: #333;
  text-align: center;
}

.loading-state {
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
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
  background-color: #fff;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  cursor: pointer;
}

.item-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.item-image {
  height: 200px;
  overflow: hidden;
  position: relative;
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
  padding: 3px 8px;
  font-size: 12px;
  color: #fff;
  background-color: #67c23a;
  border-radius: 4px;
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
  margin: 0 0 8px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.price {
  font-weight: bold;
  color: #f56c6c;
  font-size: 18px;
  margin-bottom: 8px;
}

.description {
  color: #606266;
  margin-bottom: 10px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  font-size: 14px;
  line-height: 1.4;
}

.item-meta {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 12px;
  color: #909399;
}

.item-footer {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #909399;
  border-top: 1px solid #f0f0f0;
  padding-top: 8px;
}

.views {
  display: flex;
  align-items: center;
  gap: 4px;
}

.empty-state {
  margin-top: 40px;
  padding: 20px;
}

.empty-hint {
  color: #909399;
  font-size: 14px;
  margin-top: 5px;
}

.pagination-container {
  margin-top: 30px;
  display: flex;
  justify-content: center;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .items-grid {
    grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
  }
}

@media (max-width: 480px) {
  .items-grid {
    grid-template-columns: 1fr;
  }
}
</style> 