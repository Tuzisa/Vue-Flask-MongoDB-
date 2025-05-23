<template>
  <div class="notification-wrapper">
    <el-popover
      placement="bottom"
      :width="320"
      trigger="click"
      :visible="popoverVisible"
      @show="loadUnreadMessages"
      @hide="popoverVisible = false"
    >
      <template #reference>
        <el-badge :value="totalUnread" :hidden="totalUnread === 0" class="notification-badge">
          <el-button circle class="notification-icon">
            <el-icon><Bell /></el-icon>
          </el-button>
        </el-badge>
      </template>
      
      <template #default>
        <div class="notification-header">
          <h3>消息通知</h3>
          <el-button 
            v-if="unreadMessages.length > 0" 
            link 
            type="primary" 
            @click="markAllAsRead"
          >全部已读</el-button>
        </div>
        
        <div class="notification-content">
          <div v-if="loading" class="loading-state">
            <el-skeleton :rows="3" animated />
          </div>
          <div v-else-if="unreadMessages.length === 0" class="empty-state">
            <el-empty description="暂无未读消息" :image-size="60" />
          </div>
          <div v-else class="message-list">
            <div 
              v-for="message in unreadMessages" 
              :key="message.id" 
              class="message-item"
              @click="goToItem(message.itemId)"
            >
              <el-avatar size="small" icon="User" class="sender-avatar"></el-avatar>
              <div class="message-info">
                <div class="message-sender">{{ message.senderName }}</div>
                <div class="message-preview">{{ message.content }}</div>
                <div class="message-time">{{ formatTime(message.timestamp) }}</div>
              </div>
            </div>
          </div>
        </div>
        
        <div v-if="unreadMessages.length > 0" class="notification-footer">
          <el-button 
            type="primary" 
            plain 
            @click="goToNotifications"
          >查看全部通知</el-button>
        </div>
      </template>
    </el-popover>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { Bell } from '@element-plus/icons-vue';
import socketService from '@/services/socket';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const authStore = useAuthStore();

// 状态变量
const loading = ref(false);
const unreadMessages = ref([]);
const popoverVisible = ref(false);
const intervalId = ref(null);

// 计算总未读消息数
const totalUnread = computed(() => {
  return unreadMessages.value.length;
});

// 在组件挂载时初始化
onMounted(() => {
  if (authStore.isAuthenticated) {
    setupSocketListeners();
    loadUnreadMessages();
    
    // 设置定时刷新 (每分钟)
    intervalId.value = setInterval(loadUnreadMessages, 60000);
  }
});

// 在组件销毁前清理
onBeforeUnmount(() => {
  if (intervalId.value) {
    clearInterval(intervalId.value);
  }
});

// 监听认证状态，当用户登录时自动加载未读消息
watch(() => authStore.isAuthenticated, (isAuth) => {
  if (isAuth) {
    loadUnreadMessages();
    setupSocketListeners();
  } else {
    unreadMessages.value = [];
    if (intervalId.value) {
      clearInterval(intervalId.value);
    }
  }
});

// 设置Socket监听器
const setupSocketListeners = () => {
  if (!socketService.connected.value) {
    console.warn("MessageNotification: Socket connection/authentication needs review as chat features are removed.");
  }
  
  // 监听新消息
  console.warn("MessageNotification: onNewMessage listener needs to be updated for new notification types.");
};

// 加载未读消息
const loadUnreadMessages = async () => {
  if (!authStore.isAuthenticated) return;
  
  loading.value = true;
  console.warn("MessageNotification: loadUnreadMessages logic needs to be reimplemented for general notifications or removed.");
  unreadMessages.value = [];
  loading.value = false;
};

// 将所有消息标记为已读
const markAllAsRead = async () => {
  if (unreadMessages.value.length === 0) return;
  console.warn("MessageNotification: markAllAsRead logic needs to be reimplemented for general notifications or removed.");
  unreadMessages.value = [];
  ElMessage.info('通知功能暂不可用');
  popoverVisible.value = false;
};

// 前往聊天页面
const goToItem = (itemId) => {
  popoverVisible.value = false;
  if (itemId) {
    console.warn("MessageNotification: goToItem navigation needs review or reimplementation.");
    ElMessage.info('跳转功能暂不可用');
  } else {
    console.warn("MessageNotification: No itemId provided for navigation.");
  }
};

// 前往消息列表页面
const goToNotifications = () => {
  popoverVisible.value = false;
  console.warn("MessageNotification: goToNotifications navigation needs a target page or removal.");
  ElMessage.info('通知列表暂不可用');
};

// 格式化时间
const formatTime = (timestamp) => {
  if (!timestamp) return '';
  
  const msgDate = new Date(timestamp);
  const now = new Date();
  const diffMinutes = Math.floor((now - msgDate) / (1000 * 60));
  
  if (diffMinutes < 1) {
    return '刚刚';
  } else if (diffMinutes < 60) {
    return `${diffMinutes}分钟前`;
  } else if (diffMinutes < 24 * 60) {
    return `${Math.floor(diffMinutes / 60)}小时前`;
  } else if (diffMinutes < 48 * 60) {
    return '昨天';
  } else {
    return msgDate.toLocaleDateString('zh-CN', {
      month: 'numeric',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }
};
</script>

<style scoped>
.notification-wrapper {
  display: inline-block;
}

.notification-badge :deep(.el-badge__content) {
  background-color: #f56c6c;
}

.notification-icon {
  font-size: 18px;
  color: #606266;
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 10px;
  border-bottom: 1px solid #ebeef5;
}

.notification-header h3 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}

.notification-content {
  max-height: 300px;
  overflow-y: auto;
  margin: 10px 0;
}

.loading-state, .empty-state {
  padding: 20px 0;
}

.message-list {
  padding: 5px 0;
}

.message-item {
  padding: 10px;
  display: flex;
  align-items: flex-start;
  border-bottom: 1px solid #ebeef5;
  cursor: pointer;
  transition: background-color 0.3s;
}

.message-item:hover {
  background-color: #f5f7fa;
}

.message-item:last-child {
  border-bottom: none;
}

.sender-avatar {
  margin-right: 10px;
  flex-shrink: 0;
}

.message-info {
  flex: 1;
  overflow: hidden;
}

.message-sender {
  font-weight: 500;
  margin-bottom: 5px;
  color: #303133;
}

.message-preview {
  font-size: 12px;
  color: #606266;
  margin-bottom: 5px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.message-time {
  font-size: 11px;
  color: #909399;
}

.notification-footer {
  text-align: center;
  padding-top: 10px;
  border-top: 1px solid #ebeef5;
}
</style> 