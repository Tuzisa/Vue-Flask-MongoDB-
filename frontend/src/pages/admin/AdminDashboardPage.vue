<template>
  <div class="admin-dashboard">
    <el-container>
      <el-aside width="200px">
        <div class="admin-sidebar">
          <div class="admin-logo">
            <h3>管理员后台</h3>
          </div>
          <el-menu
            :default-active="activeMenu"
            class="admin-menu"
            router
            background-color="#304156"
            text-color="#bfcbd9"
            active-text-color="#409EFF"
          >
            <el-menu-item index="/admin/dashboard">
              <el-icon><DataBoard /></el-icon>
              <span>仪表盘</span>
            </el-menu-item>
            <el-menu-item index="/admin/users">
              <el-icon><User /></el-icon>
              <span>用户管理</span>
            </el-menu-item>
            <el-menu-item index="/admin/items">
              <el-icon><Goods /></el-icon>
              <span>商品管理</span>
            </el-menu-item>
            <el-menu-item index="/admin/comments">
              <el-icon><ChatDotRound /></el-icon>
              <span>评论管理</span>
            </el-menu-item>
            <el-menu-item @click="logout">
              <el-icon><SwitchButton /></el-icon>
              <span>退出登录</span>
            </el-menu-item>
          </el-menu>
        </div>
      </el-aside>
      
      <el-container>
        <el-header>
          <div class="admin-header">
            <div class="admin-breadcrumb">
              <el-breadcrumb separator="/">
                <el-breadcrumb-item :to="{ path: '/admin/dashboard' }">首页</el-breadcrumb-item>
                <el-breadcrumb-item v-if="$route.name === 'AdminUserManage'">用户管理</el-breadcrumb-item>
                <el-breadcrumb-item v-if="$route.name === 'AdminItemManage'">商品管理</el-breadcrumb-item>
                <el-breadcrumb-item v-if="$route.name === 'AdminCommentManage'">评论管理</el-breadcrumb-item>
              </el-breadcrumb>
            </div>
            <div class="admin-user">
              <span>{{ authStore.username }}</span>
              <el-avatar 
                :size="32" 
                :src="authStore.user?.avatar_url || '/images/moren.jpg'"
              />
            </div>
          </div>
        </el-header>
        
        <el-main>
          <router-view v-if="$route.name !== 'AdminDashboard'" />
          <div v-else class="dashboard-content">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-card class="dashboard-card" shadow="hover">
                  <template #header>
                    <div class="card-header">
                      <span>用户总数</span>
                      <el-tag size="small" type="primary">用户</el-tag>
                    </div>
                  </template>
                  <div class="card-content">
                    <el-statistic :value="stats.total_users" :loading="loading">
                      <template #suffix>
                        <el-icon><User /></el-icon>
                      </template>
                    </el-statistic>
                    <div class="stat-info">
                      <span>最近7天新增: {{ stats.new_users_count || 0 }}</span>
                    </div>
                    <el-button type="primary" size="small" @click="router.push('/admin/users')">
                      管理用户
                    </el-button>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="8">
                <el-card class="dashboard-card" shadow="hover">
                  <template #header>
                    <div class="card-header">
                      <span>商品总数</span>
                      <el-tag size="small" type="success">商品</el-tag>
                    </div>
                  </template>
                  <div class="card-content">
                    <el-statistic :value="stats.total_items" :loading="loading">
                      <template #suffix>
                        <el-icon><Goods /></el-icon>
                      </template>
                    </el-statistic>
                    <div class="stat-info">
                      <span>最近7天新增: {{ stats.new_items_count || 0 }}</span>
                    </div>
                    <el-button type="success" size="small" @click="router.push('/admin/items')">
                      管理商品
                    </el-button>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="8">
                <el-card class="dashboard-card" shadow="hover">
                  <template #header>
                    <div class="card-header">
                      <span>评论总数</span>
                      <el-tag size="small" type="warning">评论</el-tag>
                    </div>
                  </template>
                  <div class="card-content">
                    <el-statistic :value="stats.total_comments" :loading="loading">
                      <template #suffix>
                        <el-icon><ChatDotRound /></el-icon>
                      </template>
                    </el-statistic>
                    <div class="stat-info">
                      <span>系统评论</span>
                    </div>
                    <el-button type="warning" size="small" @click="router.push('/admin/comments')">
                      管理评论
                    </el-button>
                  </div>
                </el-card>
              </el-col>
            </el-row>
            
            <el-row :gutter="20" class="mt-20">
              <el-col :span="24">
                <el-card shadow="hover">
                  <template #header>
                    <div class="card-header">
                      <span>数据统计</span>
                      <el-button type="primary" size="small" plain @click="loadStats">刷新数据</el-button>
                    </div>
                  </template>
                  <div class="stats-grid">
                    <div class="stat-item">
                      <h4>用户活跃度</h4>
                      <div class="stat-content">
                        <div class="stat-row">
                          <span>新增用户</span>
                          <el-tag size="small" type="success">{{ stats.new_users_count || 0 }} 人</el-tag>
                        </div>
                        <div class="stat-row">
                          <span>总用户数</span>
                          <el-tag size="small" type="info">{{ stats.total_users || 0 }} 人</el-tag>
                        </div>
                      </div>
                    </div>
                    
                    <div class="stat-item">
                      <h4>商品数据</h4>
                      <div class="stat-content">
                        <div class="stat-row">
                          <span>新增商品</span>
                          <el-tag size="small" type="success">{{ stats.new_items_count || 0 }} 个</el-tag>
                        </div>
                        <div class="stat-row">
                          <span>总商品数</span>
                          <el-tag size="small" type="info">{{ stats.total_items || 0 }} 个</el-tag>
                        </div>
                      </div>
                    </div>
                    
                    <div class="stat-item">
                      <h4>评论数据</h4>
                      <div class="stat-content">
                        <div class="stat-row">
                          <span>总评论数</span>
                          <el-tag size="small" type="info">{{ stats.total_comments || 0 }} 条</el-tag>
                        </div>
                        <div class="stat-row">
                          <span>评论率</span>
                          <el-tag size="small" type="warning">
                            {{ calculateCommentRate() }}%
                          </el-tag>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div class="refresh-info">
                    <el-tag size="small" type="info">最后更新时间: {{ lastUpdateTime }}</el-tag>
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </div>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { ElMessage, ElMessageBox } from 'element-plus';
import { adminApi } from '@/services/api';
import { 
  User, 
  Goods, 
  DataBoard, 
  SwitchButton,
  ChatDotRound
} from '@element-plus/icons-vue';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

// 活动菜单项
const activeMenu = computed(() => route.path);

// 统计数据
const stats = ref({
  total_users: 0,
  total_items: 0,
  total_comments: 0,
  new_users_count: 0,
  new_items_count: 0
});

const loading = ref(false);
const lastUpdateTime = ref(new Date().toLocaleString());

// 初始化
onMounted(() => {
  // 检查是否是管理员
  if (!authStore.isAdmin) {
    ElMessage.error('您没有管理员权限');
    router.push('/admin');
    return;
  }
  
  // 加载统计数据
  loadStats();
});

// 加载统计数据
const loadStats = async () => {
  loading.value = true;
  try {
    const response = await adminApi.getDashboardStats();
    stats.value = response.data;
    lastUpdateTime.value = new Date().toLocaleString();
    ElMessage.success('数据加载成功');
  } catch (error) {
    console.error('加载统计数据失败:', error);
    ElMessage.error('加载统计数据失败，请稍后重试');
  } finally {
    loading.value = false;
  }
};

// 计算评论率
const calculateCommentRate = () => {
  if (!stats.value.total_items || stats.value.total_items === 0) {
    return '0.00';
  }
  const rate = (stats.value.total_comments / stats.value.total_items) * 100;
  return rate.toFixed(2);
};

// 退出登录
const logout = () => {
  ElMessageBox.confirm('确定要退出管理员登录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    authStore.logout();
    router.push('/admin');
    ElMessage.success('已退出管理员登录');
  }).catch(() => {});
};
</script>

<style scoped>
.admin-dashboard {
  height: 100vh;
}

.admin-sidebar {
  height: 100%;
  background-color: #304156;
  color: #fff;
}

.admin-logo {
  height: 60px;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #2b3649;
}

.admin-logo h3 {
  margin: 0;
  font-size: 18px;
  color: #fff;
}

.admin-menu {
  border-right: none;
}

.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  border-bottom: 1px solid #e6e6e6;
}

.admin-user {
  display: flex;
  align-items: center;
  gap: 10px;
}

.el-header {
  background-color: #fff;
  padding: 0 20px;
}

.el-main {
  background-color: #f0f2f5;
  padding: 20px;
}

.dashboard-content {
  margin-top: 20px;
}

.dashboard-card {
  margin-bottom: 20px;
  transition: all 0.3s;
}

.dashboard-card:hover {
  transform: translateY(-5px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-content {
  text-align: center;
  padding: 20px 0;
}

.stat-info {
  margin: 10px 0;
  font-size: 14px;
  color: #909399;
}

.mt-20 {
  margin-top: 20px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  padding: 20px 0;
}

.stat-item {
  text-align: center;
  padding: 15px;
  border-radius: 8px;
  background-color: #f8f9fa;
}

.stat-item h4 {
  margin: 0 0 15px 0;
  color: #606266;
}

.stat-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 5px 15px;
}

.stat-row span {
  color: #606266;
}

.refresh-info {
  text-align: right;
  padding: 10px 0;
  margin-top: 10px;
  border-top: 1px solid #ebeef5;
}
</style> 