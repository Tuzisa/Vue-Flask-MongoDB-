<template>
  <div class="app-container">
    <connection-status-bar />
    <header-component v-if="$route.name && !hiddenHeader.includes($route.name)" />
    <global-notification ref="notification" />
    <div class="main-content">
      <router-view />
    </div>
    <footer-component v-if="$route.name && !hiddenFooter.includes($route.name)" />
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth';
import { computed, onMounted, ref, provide, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import MessageNotification from '@/components/MessageNotification.vue';
import ConnectionStatusBar from '@/components/ConnectionStatusBar.vue';
import GlobalNotification from '@/components/GlobalNotification.vue';
import HeaderComponent from '@/components/HeaderComponent.vue';
import FooterComponent from '@/components/FooterComponent.vue';
import { ElMessage } from 'element-plus';

const authStore = useAuthStore();
const route = useRoute();
const router = useRouter();
const notification = ref(null);

// 定义哪些页面不显示页头和页脚
const hiddenHeader = ref(['LoginRegister']);
const hiddenFooter = ref(['LoginRegister']);

const isAuthenticated = computed(() => authStore.isAuthenticated);

// 检查token是否过期
onMounted(() => {
  if (isAuthenticated.value) {
    authStore.checkTokenExpiration();
  }
  // 初始化认证状态
  authStore.initialize();
});

// 监听路由变化，更新未读消息数量
watch(() => route.path, () => {
  if (isAuthenticated.value) {
  }
});

// 将通知服务提供给整个应用
provide('notification', {
  success: (title, message, duration) => notification.value?.success(title, message, duration),
  error: (title, message, duration) => notification.value?.error(title, message, duration),
  warning: (title, message, duration) => notification.value?.warning(title, message, duration),
  info: (title, message, duration) => notification.value?.info(title, message, duration)
});

// 创建全局通知方法
window.$notify = {
  success: (title, message, duration) => {
    window.dispatchEvent(new CustomEvent('notification', {
      detail: { type: 'success', title, message, duration }
    }));
  },
  error: (title, message, duration) => {
    window.dispatchEvent(new CustomEvent('notification', {
      detail: { type: 'error', title, message, duration }
    }));
  },
  warning: (title, message, duration) => {
    window.dispatchEvent(new CustomEvent('notification', {
      detail: { type: 'warning', title, message, duration }
    }));
  },
  info: (title, message, duration) => {
    window.dispatchEvent(new CustomEvent('notification', {
      detail: { type: 'info', title, message, duration }
    }));
  }
};
</script>

<style>
/* 全局样式 */
body {
  margin: 0;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', '微软雅黑', sans-serif;
  color: #333;
  background-color: #f8f8f8;
}

.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.main-content {
  flex: 1;
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}

header {
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
  background-color: #fff;
}

.nav-menu {
  max-width: 1200px;
  margin: 0 auto;
}

.flex-grow {
  flex-grow: 1;
}

.status-container,
.notification-container {
  display: flex;
  align-items: center;
  margin: 0 10px;
}

footer {
  text-align: center;
  padding: 20px 0;
  background-color: #f9f9f9;
  border-top: 1px solid #eee;
  margin-top: 20px;
  color: #666;
}
</style> 