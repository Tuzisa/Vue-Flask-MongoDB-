<template>
  <div class="global-notification-wrapper">
    <transition-group name="fade">
      <div 
        v-for="notification in notifications" 
        :key="notification.id" 
        class="notification-item"
        :class="`notification-${notification.type}`"
      >
        <div class="notification-icon">
          <el-icon v-if="notification.type === 'success'"><SuccessFilled /></el-icon>
          <el-icon v-else-if="notification.type === 'warning'"><WarningFilled /></el-icon>
          <el-icon v-else-if="notification.type === 'error'"><CircleCloseFilled /></el-icon>
          <el-icon v-else><InfoFilled /></el-icon>
        </div>
        <div class="notification-content">
          <div class="notification-title">{{ notification.title }}</div>
          <div v-if="notification.message" class="notification-message">{{ notification.message }}</div>
        </div>
        <div class="notification-close" @click="removeNotification(notification.id)">
          <el-icon><Close /></el-icon>
        </div>
      </div>
    </transition-group>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { SuccessFilled, WarningFilled, CircleCloseFilled, InfoFilled, Close } from '@element-plus/icons-vue';

const notifications = ref([]);
let notificationId = 0;

// 添加通知
const addNotification = (type, title, message = '', duration = 4000) => {
  const id = notificationId++;
  notifications.value.push({ id, type, title, message });
  
  if (duration > 0) {
    setTimeout(() => {
      removeNotification(id);
    }, duration);
  }
  
  return id;
};

// 移除通知
const removeNotification = (id) => {
  const index = notifications.value.findIndex(item => item.id === id);
  if (index !== -1) {
    notifications.value.splice(index, 1);
  }
};

// 创建快捷方法
const success = (title, message, duration) => addNotification('success', title, message, duration);
const error = (title, message, duration) => addNotification('error', title, message, duration);
const warning = (title, message, duration) => addNotification('warning', title, message, duration);
const info = (title, message, duration) => addNotification('info', title, message, duration);

// 暴露方法给组件外部使用
defineExpose({
  success,
  error,
  warning,
  info,
  removeNotification
});

// 挂载全局 eventBus 监听
onMounted(() => {
  window.addEventListener('notification', (event) => {
    const { type, title, message, duration } = event.detail;
    addNotification(type, title, message, duration);
  });
});
</script>

<style scoped>
.global-notification-wrapper {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  width: 300px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.notification-item {
  display: flex;
  align-items: flex-start;
  padding: 12px 15px;
  border-radius: 4px;
  box-shadow: 0 3px 6px rgba(0, 0, 0, 0.15);
  background-color: white;
  cursor: default;
  animation: slide-in 0.3s ease;
}

.notification-success {
  border-left: 4px solid #67c23a;
}

.notification-warning {
  border-left: 4px solid #e6a23c;
}

.notification-error {
  border-left: 4px solid #f56c6c;
}

.notification-info {
  border-left: 4px solid #909399;
}

.notification-icon {
  margin-right: 10px;
  margin-top: 2px;
}

.notification-success .notification-icon {
  color: #67c23a;
}

.notification-warning .notification-icon {
  color: #e6a23c;
}

.notification-error .notification-icon {
  color: #f56c6c;
}

.notification-info .notification-icon {
  color: #909399;
}

.notification-content {
  flex: 1;
}

.notification-title {
  font-weight: 500;
  margin-bottom: 3px;
}

.notification-message {
  font-size: 13px;
  color: #606266;
}

.notification-close {
  cursor: pointer;
  color: #909399;
  padding: 3px;
}

.notification-close:hover {
  color: #606266;
}

/* 动画 */
.fade-enter-active,
.fade-leave-active {
  transition: all 0.3s ease;
}

.fade-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.fade-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

@keyframes slide-in {
  from {
    transform: translateX(30px);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}
</style> 