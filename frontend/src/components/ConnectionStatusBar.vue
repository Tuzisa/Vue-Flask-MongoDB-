<template>
  <div
    v-if="showBar"
    class="connection-status-bar"
    :class="statusClass"
  >
    <el-icon class="status-icon"><component :is="statusIcon" /></el-icon>
    <span class="status-message">{{ statusMessage }}</span>
    <el-button v-if="status === 'offline'" type="primary" size="small" @click="reloadPage">
      重新加载
    </el-button>
    <el-icon class="close-icon" @click="dismiss"><Close /></el-icon>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
import { 
  WarningFilled, 
  CircleCloseFilled, 
  Loading, 
  Connection, 
  Close 
} from '@element-plus/icons-vue';

// 状态
const status = ref('online'); // 'online', 'unstable', 'offline'
const showBar = ref(false);
const dismissedTimestamp = ref(0);

// 计算属性
const statusIcon = computed(() => {
  switch (status.value) {
    case 'offline':
      return CircleCloseFilled;
    case 'unstable':
      return WarningFilled;
    case 'reconnecting':
      return Loading;
    default:
      return Connection;
  }
});

const statusClass = computed(() => {
  return `status-${status.value}`;
});

const statusMessage = computed(() => {
  switch (status.value) {
    case 'offline':
      return '网络连接已断开，请检查您的网络设置';
    case 'unstable':
      return '网络连接不稳定，部分功能可能受影响';
    case 'reconnecting':
      return '正在尝试重新连接...';
    default:
      return '网络连接正常';
  }
});

// 检查连接状态
const checkConnectionStatus = () => {
  // 检查是否在线
  const isOnline = navigator.onLine;
  
  // 检查连接不稳定（从axios拦截器获取）
  const connectionFailures = window.connectionFailures || 0;
  
  if (!isOnline) {
    status.value = 'offline';
    showBar.value = true;
  } else if (connectionFailures > 2) {
    status.value = 'unstable';
    showBar.value = true;
  } else {
    // 正常连接
    status.value = 'online';
    
    // 只有在之前显示了错误状态时才隐藏
    if (showBar.value && status.value === 'online') {
      setTimeout(() => {
        showBar.value = false;
      }, 3000);
    }
  }
};

// 关闭通知
const dismiss = () => {
  showBar.value = false;
  dismissedTimestamp.value = Date.now();
};

// 重新加载页面
const reloadPage = () => {
  window.location.reload();
};

// 事件监听器
const handleOnline = () => {
  status.value = 'online';
  setTimeout(() => {
    checkConnectionStatus();
  }, 2000);
};

const handleOffline = () => {
  status.value = 'offline';
  showBar.value = true;
};

// 定期检查连接状态
let statusCheckInterval;

// 组件挂载时添加事件监听
onMounted(() => {
  window.addEventListener('online', handleOnline);
  window.addEventListener('offline', handleOffline);
  
  // 初始检查
  checkConnectionStatus();
  
  // 定期检查（每10秒）
  statusCheckInterval = setInterval(() => {
    // 只有在未被用户手动关闭的情况下才检查
    const timeSinceDismissal = Date.now() - dismissedTimestamp.value;
    if (timeSinceDismissal > 30000) { // 30秒后才能再次显示
      checkConnectionStatus();
    }
  }, 10000);
});

// 组件卸载时移除事件监听
onBeforeUnmount(() => {
  window.removeEventListener('online', handleOnline);
  window.removeEventListener('offline', handleOffline);
  clearInterval(statusCheckInterval);
});
</script>

<style scoped>
.connection-status-bar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 9999;
  padding: 8px 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  transition: all 0.3s ease;
  color: #fff;
}

.status-online {
  background-color: #67c23a;
}

.status-unstable {
  background-color: #e6a23c;
}

.status-offline, .status-error {
  background-color: #f56c6c;
}

.status-reconnecting {
  background-color: #409eff;
}

.status-icon {
  margin-right: 8px;
  font-size: 18px;
}

.status-message {
  flex: 1;
}

.close-icon {
  margin-left: 16px;
  cursor: pointer;
  font-size: 16px;
}

.close-icon:hover {
  opacity: 0.8;
}
</style> 