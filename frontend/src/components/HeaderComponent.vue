<template>
  <header class="site-header">
    <el-menu 
      class="nav-menu" 
      mode="horizontal" 
      :router="true" 
      :ellipsis="false"
      :default-active="activeRoute"
    >
      <div class="logo-container">
        <img src="/images/logo.png" alt="网站Logo" class="site-logo">
      </div>
      <el-menu-item index="/">
        <el-icon><House /></el-icon>
        首页
      </el-menu-item>
      <el-menu-item index="/items">
        <el-icon><ShoppingBag /></el-icon>
        商品列表
      </el-menu-item>
      <div class="flex-grow"></div>
      <template v-if="isAuthenticated">
        <el-menu-item index="/publish">
          <el-icon><Plus /></el-icon>
          发布商品
        </el-menu-item>
        
        <el-sub-menu>
          <template #title>
            <el-avatar :size="24" :src="avatarUrl" @error="handleAvatarError">
              <el-icon><User /></el-icon>
            </el-avatar>
            {{ username }}
          </template>
          <el-menu-item index="/profile">
            <el-icon><UserFilled /></el-icon>
            个人中心
          </el-menu-item>
          <el-menu-item index="/settings">
            <el-icon><Setting /></el-icon>
            个人设置
          </el-menu-item>
          <el-menu-item @click="handleLogout">
            <el-icon><SwitchButton /></el-icon>
            退出登录
          </el-menu-item>
        </el-sub-menu>
      </template>
      <template v-else>
        <el-menu-item index="/login">
          <el-icon><Avatar /></el-icon>
          登录/注册
        </el-menu-item>
      </template>
    </el-menu>
  </header>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth';
import { computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { 
  House, 
  ShoppingBag, 
  User, 
  UserFilled,
  Plus, 
  Avatar, 
  SwitchButton,
  Setting
} from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';

const authStore = useAuthStore();
const router = useRouter();
const route = useRoute();

// 计算当前激活的路由
const activeRoute = computed(() => {
  return route.path;
});

const isAuthenticated = computed(() => authStore.isAuthenticated);
const username = computed(() => authStore.username);

// 获取头像URL
const avatarUrl = computed(() => {
  const baseUrl = import.meta.env.VITE_API_BASE_URL || '';
  if (authStore.user?.avatar) {
    return authStore.user.avatar.startsWith('/static') 
      ? `${baseUrl}${authStore.user.avatar}` 
      : authStore.user.avatar;
  }
  return `${baseUrl}/static/avatars/default_avatar.jpg`;
});

// 处理头像加载错误
const handleAvatarError = (event) => {
  const baseUrl = import.meta.env.VITE_API_BASE_URL || '';
  event.target.src = `${baseUrl}/static/avatars/default_avatar.jpg`;
};

const handleLogout = () => {
  authStore.logout();
  ElMessage.success('您已成功退出登录');
  router.push('/login');
};
</script>

<style scoped>
.site-header {
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
  background-color: #fff;
}

.nav-menu {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
}

.logo-container {
  padding: 0 15px;
  display: flex;
  align-items: center;
}

.site-logo {
  height: 40px;
  width: auto;
  margin-right: 10px;
}

.flex-grow {
  flex-grow: 1;
}
</style> 