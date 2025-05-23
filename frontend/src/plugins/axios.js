import axios from 'axios';
import { useAuthStore } from '@/stores/auth';
import { ElMessage } from 'element-plus';
import router from '@/router';

// 创建 axios 实例
const instance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/',
  timeout: 60000, // 增加到60秒，因为Base64编码的图片可能会很大
  maxContentLength: 50 * 1024 * 1024, // 允许50MB的响应大小
  maxBodyLength: 50 * 1024 * 1024,    // 允许50MB的请求体大小
  headers: {
    'Content-Type': 'application/json'
  }
});

// 请求拦截器
instance.interceptors.request.use(
  config => {
    // 从 localStorage 获取 token
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  error => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// 响应拦截器
instance.interceptors.response.use(
  response => {
    // 连接成功，重置连接失败次数
    window.connectionFailures = 0;
    return response;
  },
  error => {
    console.error('API Error:', error);
    
    // 检查是否是网络连接错误
    const isConnectionError = 
      error.code === 'ECONNABORTED' || 
      error.code === 'ECONNRESET' ||
      error.message?.includes('Network Error') ||
      !navigator.onLine;
    
    // 跟踪连接失败
    if (isConnectionError) {
      // 初始化失败计数器
      if (typeof window.connectionFailures === 'undefined') {
        window.connectionFailures = 0;
      }
      
      // 增加失败计数
      window.connectionFailures++;
      
      console.warn(`连接失败次数: ${window.connectionFailures}`);
      
      // 如果错误是由超时引起的
      if (error.code === 'ECONNABORTED' && error.message.includes('timeout')) {
        ElMessage.warning('请求超时，服务器响应时间过长');
      } else if (!navigator.onLine) {
        ElMessage.warning('网络已断开，请检查您的互联网连接');
      } else {
        ElMessage.warning('网络连接不稳定，请稍后重试');
      }
      
      // 如果是第一次失败，尝试一次自动重试
      if (window.connectionFailures === 1 && error.config && !error.config._isNetworkRetry) {
        console.log('自动重试请求...');
        
        // 标记为已重试
        error.config._isNetworkRetry = true;
        
        // 增加超时时间
        error.config.timeout = error.config.timeout * 1.5;
        
        // 延迟1秒后重试
        return new Promise(resolve => {
          setTimeout(() => {
            resolve(instance(error.config));
          }, 1000);
        });
      }
    }
    
    if (error.response) {
      // 服务器响应错误 (2xx 以外的状态码)
      const status = error.response.status;
      const data = error.response.data;
      
      console.error(`API Error ${status}:`, data);

      // 处理401错误 (未授权)
      if (status === 401) {
        // 尝试刷新 token
        const authStore = useAuthStore();
        if (authStore.token && !error.config._isRetry) {
          error.config._isRetry = true;
          
          return authStore.checkAndRefreshToken()
            .then(valid => {
              if (valid) {
                // 获取新的 token 后重试请求
                return instance(error.config);
              } else {
                // 如果刷新失败，则登出
                authStore.logout();
                ElMessage.error('登录已过期，请重新登录');
                router.push('/login');
                return Promise.reject(error);
              }
            })
            .catch(() => {
              // 刷新 token 失败，登出
              authStore.logout();
              ElMessage.error('登录已过期，请重新登录');
              router.push('/login');
              return Promise.reject(error);
            });
        } else {
          // 没有 token 或已经重试过，直接登出
          const authStore = useAuthStore();
          authStore.logout();
          ElMessage.error('请先登录');
          router.push('/login');
        }
      }
      
      // 处理特定错误消息
      if (data && data.msg) {
        ElMessage.error(data.msg);
      } else if (status === 403) {
        ElMessage.error('您没有权限执行此操作');
      } else if (status === 404) {
        ElMessage.error('请求的资源不存在');
      } else if (status === 500) {
        ElMessage.error('服务器内部错误，请稍后重试');
      } else {
        ElMessage.error(`请求失败 (${status})`);
      }
    } else if (error.request) {
      // 请求发出但没有收到响应
      console.error('No response received:', error.request);
      ElMessage.error('服务器无响应，请检查网络连接');
    } else {
      // 设置请求时出现错误
      console.error('Request error:', error.message);
      ElMessage.error('请求失败，请稍后重试');
    }
    
    return Promise.reject(error);
  }
);

// 错误消息显示时间限制
const messageQueue = new Set();
const maxQueueSize = 3;
const messageTimeout = 3000;

// 覆盖 ElMessage 以限制同时显示的消息数量
const originalError = ElMessage.error;
ElMessage.error = (message) => {
  if (messageQueue.size >= maxQueueSize) {
    return;
  }
  
  messageQueue.add(message);
  const msgInstance = originalError(message);
  
  setTimeout(() => {
    messageQueue.delete(message);
  }, messageTimeout);
  
  return msgInstance;
};

// 导出 axios 实例
export default instance; 