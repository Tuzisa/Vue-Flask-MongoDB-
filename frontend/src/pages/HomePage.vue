<template>
  <div class="home-container">
    <!-- 欢迎横幅 -->
    <div class="welcome-banner">
      <h1>欢迎来到Two手交易平台</h1>
      <p>发现独特宝贝，享受优质Two手交易体验</p>
      <el-button type="primary" size="large" @click="goToItems">立即浏览</el-button>
    </div>
    
    <!-- 轮播图 -->
    <el-carousel height="400px" class="home-carousel">
      <el-carousel-item v-for="(item, index) in carouselItems" :key="index">
        <div class="carousel-content" :style="{ 'background-image': `url(${item.image})` }">
          <div class="carousel-info">
            <h2>{{ item.title }}</h2>
            <p>{{ item.description }}</p>
            <el-button type="primary" @click="navigateTo(item.link)">查看详情</el-button>
          </div>
        </div>
      </el-carousel-item>
    </el-carousel>
    
    <!-- 分类快速访问 -->
    <div class="categories-section">
      <h2 class="section-title">热门分类</h2>
      <div class="categories-grid">
        <div 
          v-for="(category, index) in categories" 
          :key="index" 
          class="category-card"
          @click="navigateToCategory(category.value)"
        >
          <el-icon :size="40" class="category-icon">
            <component :is="category.icon" />
          </el-icon>
          <h3>{{ category.name }}</h3>
        </div>
      </div>
    </div>
    
    <!-- 最新动态区域 -->
    <div class="news-section">
      <h2 class="section-title">平台公告</h2>
      <div class="news-cards">
        <el-card v-for="(news, index) in newsItems" :key="index" class="news-card">
          <template #header>
            <div class="news-header">
              <h3>{{ news.title }}</h3>
              <small>{{ formatDate(news.date) }}</small>
            </div>
          </template>
          <div class="news-content">
            <p>{{ news.content }}</p>
          </div>
        </el-card>
      </div>
    </div>
    
    <!-- 使用说明区域 -->
    <div class="how-it-works">
      <h2 class="section-title">如何使用</h2>
      <div class="steps-container">
        <div class="step">
          <div class="step-icon">
            <el-icon :size="50"><UserFilled /></el-icon>
          </div>
          <h3>1. 注册账号</h3>
          <p>创建账号开始您的Two手交易之旅</p>
        </div>
        <div class="step">
          <div class="step-icon">
            <el-icon :size="50"><Plus /></el-icon>
          </div>
          <h3>2. 发布商品</h3>
          <p>几分钟内轻松发布您的闲置物品</p>
        </div>
        <div class="step">
          <div class="step-icon">
            <el-icon :size="50"><Comment /></el-icon>
          </div>
          <h3>3. 沟通交流</h3>
          <p>与买家/卖家快速沟通达成交易</p>
        </div>
        <div class="step">
          <div class="step-icon">
            <el-icon :size="50"><Goods /></el-icon>
          </div>
          <h3>4. 完成交易</h3>
          <p>安全便捷地完成交易过程</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { 
  Goods, View, UserFilled, Plus, Comment,
  Monitor, Tickets, Collection, Basketball, Handbag 
} from '@element-plus/icons-vue';

const router = useRouter();
const authStore = useAuthStore();
const isAuthenticated = computed(() => authStore.isAuthenticated);

// 轮播图数据
const carouselItems = [
  {
    title: "高品质二手电子产品",
    description: "发现各种品牌的二手电子产品，价格实惠，品质保证",
    image: "https://images.unsplash.com/photo-1468495244123-6c6c332eeece?q=80&w=1000",
    link: "/items?category=electronics"
  },
  {
    title: "精选时尚服饰",
    description: "浏览各类二手服装、鞋帽、配饰，找到适合您的时尚单品",
    image: "https://images.unsplash.com/photo-1567401893414-76b7b1e5a7a5?q=80&w=1000",
    link: "/items?category=clothing"
  },
  {
    title: "二手图书专区",
    description: "各类珍藏书籍，让知识流转起来",
    image: "https://images.unsplash.com/photo-1507842217343-583bb7270b66?q=80&w=1000",
    link: "/items?category=books"
  }
];

// 分类数据
const categories = [
  { name: "电子产品", value: "electronics", icon: Monitor },
  { name: "服装", value: "clothing", icon: Handbag },
  { name: "图书", value: "books", icon: Tickets },
  { name: "家具", value: "furniture", icon: Collection },
  { name: "其他", value: "other", icon: Basketball }
];

// 新闻公告
const newsItems = [
  {
    title: "平台全新升级",
    date: new Date(2023, 10, 15),
    content: "我们的平台已完成全新升级，带来更流畅的用户体验和更多功能。"
  },
  {
    title: "防诈骗提醒",
    date: new Date(2023, 11, 1),
    content: "请注意防范交易诈骗，不要轻信任何要求线下付款的陌生人。"
  },
  {
    title: "年末促销活动",
    date: new Date(2023, 11, 20),
    content: "年末大促即将开始，关注我们获取更多优惠信息。"
  }
];

// 组件初始化
onMounted(async () => {
  // loadFeaturedItems(); // 移除加载推荐商品调用
});

// 导航到商品列表
const goToItems = () => {
  router.push('/items');
};

// 导航到指定链接
const navigateTo = (link) => {
  router.push(link);
};

// 导航到分类
const navigateToCategory = (category) => {
  router.push(`/items?category=${category}`);
};

// 查看商品详情
const viewItemDetail = (itemId) => {
  router.push({ name: 'ItemDetail', params: { id: itemId } });
};

// 获取商品图片URL
const getItemImageUrl = (item) => {
  if (!item) return '';
  
  // 使用itemHelpers中的getImageUrl方法（如果存在）
  // if (apiService.itemHelpers && apiService.itemHelpers.getImageUrl) { // itemHelpers 可能也不再需要导入
  //   return apiService.itemHelpers.getImageUrl(item);
  // }
  
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
</script>

<style scoped>
.home-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  position: relative;
}

.welcome-banner {
  text-align: center;
  padding: 40px 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 30px;
}

.welcome-banner h1 {
  font-size: 2.5rem;
  margin-bottom: 15px;
  color: #409EFF;
}

.welcome-banner p {
  font-size: 1.2rem;
  color: #606266;
  margin-bottom: 25px;
}

.home-carousel {
  margin-bottom: 40px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.carousel-content {
  height: 100%;
  background-size: cover;
  background-position: center;
  display: flex;
  align-items: center;
  padding: 0 50px;
}

.carousel-info {
  background-color: rgba(255, 255, 255, 0.8);
  padding: 30px;
  border-radius: 8px;
  max-width: 450px;
}

.carousel-info h2 {
  font-size: 1.8rem;
  margin-bottom: 10px;
  color: #303133;
}

.carousel-info p {
  font-size: 1rem;
  margin-bottom: 20px;
  color: #606266;
}

.section-title {
  text-align: center;
  font-size: 1.8rem;
  margin-bottom: 30px;
  position: relative;
  color: #303133;
}

.section-title::after {
  content: '';
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 60px;
  height: 3px;
  background-color: #409EFF;
}

.categories-section {
  margin-bottom: 40px;
}

.categories-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 20px;
}

.category-card {
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  text-align: center;
  cursor: pointer;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.category-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
}

.category-icon {
  margin-bottom: 15px;
  color: #409EFF;
}

.category-card h3 {
  margin: 0;
  font-size: 1rem;
  color: #303133;
}

.news-section {
  margin-bottom: 40px;
}

.news-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.news-card {
  height: 100%;
}

.news-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.news-header h3 {
  margin: 0;
  font-size: 1.1rem;
  color: #303133;
}

.news-header small {
  color: #909399;
}

.news-content {
  color: #606266;
}

.how-it-works {
  margin-bottom: 40px;
}

.steps-container {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.step {
  text-align: center;
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.step-icon {
  margin-bottom: 15px;
  color: #409EFF;
}

.step h3 {
  margin: 0 0 10px 0;
  color: #303133;
}

.step p {
  margin: 0;
  color: #606266;
}

/* 移除 featured-section 和 featured-grid 的样式 */
/*
.featured-section {
  margin-bottom: 40px;
}

.featured-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.featured-item {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.featured-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
}

.featured-image {
  height: 180px;
  overflow: hidden;
}

.featured-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.featured-info {
  padding: 15px;
}

.featured-info h3 {
  margin: 0 0 10px 0;
  font-size: 1rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #303133;
}

.featured-info .price {
  font-weight: bold;
  color: #f56c6c;
  margin-bottom: 10px;
}

.featured-meta {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
  color: #909399;
}
*/

.views {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 移除响应式调整中与 featured-grid 相关的部分 */
/*
@media (max-width: 992px) {
  .categories-grid {
    grid-template-columns: repeat(3, 1fr);
  }
  
  .featured-grid {
    grid-template-columns: repeat(3, 1fr);
  }
  
  .news-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .steps-container {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .featured-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .carousel-info {
    max-width: 100%;
    padding: 20px;
  }
  
  .carousel-info h2 {
    font-size: 1.5rem;
  }
}

@media (max-width: 576px) {
  .categories-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .featured-grid {
    grid-template-columns: 1fr;
  }
  
  .news-cards {
    grid-template-columns: 1fr;
  }
  
  .steps-container {
    grid-template-columns: 1fr;
  }
}
*/

.loading-state {
  grid-column: span 4; /* 这个可能也需要调整或移除，如果它是特定于 featured-grid 的 */
  padding: 20px;
}
</style> 