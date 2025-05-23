import { defineStore } from 'pinia'
import { ref, computed, watch, onMounted } from 'vue'
import axios from 'axios' // 假设你会创建一个 axios 实例
import { userApi } from '@/services/api'
import socketService from '@/services/socket'

// 定义认证相关的 Store
export const useAuthStore = defineStore('auth', () => {
  // 状态
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  const loading = ref(false)
  const error = ref(null)

  // Getters
  const isAuthenticated = computed(() => !!token.value)
  const userId = computed(() => user.value ? user.value.id : null)
  const username = computed(() => user.value ? user.value.username : null)
  const isAdmin = computed(() => {
    if (!user.value) return false;
    // 检查用户是否有管理员角色或is_admin标志
    return user.value.role === 'admin' || 
           user.value.is_admin === true || 
           (user.value.email === 'admin@example.com') ||
           (user.value.username === 'admin'); // 添加用户名检查
  });

  function setToken(newToken) {
    token.value = newToken
    if (newToken) {
      localStorage.setItem('token', newToken)
      axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`
    } else {
      localStorage.removeItem('token')
      delete axios.defaults.headers.common['Authorization']
    }
    isAuthenticated.value = !!newToken
  }

  function setUser(newUser) {
    user.value = newUser
    if (newUser) {
      localStorage.setItem('user', JSON.stringify(newUser))
    } else {
      localStorage.removeItem('user')
    }
  }

  // 检查并刷新令牌
  async function checkAndRefreshToken() {
    if (!token.value) return false
    
    try {
      // 解析JWT获取过期时间
      const base64Url = token.value.split('.')[1]
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
      const payload = JSON.parse(window.atob(base64))
      
      // 检查令牌是否过期
      const now = Math.floor(Date.now() / 1000)
      const timeUntilExpiry = payload.exp - now
      
      // 如果令牌已过期
      if (timeUntilExpiry <= 0) {
        console.log('Token expired, logging out')
        logout()
        return false
      }
      
      // 如果令牌即将过期 (5分钟内)，刷新它
      if (timeUntilExpiry < 300) {
        console.log('Token about to expire, refreshing...')
        const response = await userApi.refreshToken()
        if (response.data && response.data.access_token) {
          setToken(response.data.access_token)
          
          // 重新连接 Socket
          if (socketService.connected.value) {
            socketService.disconnect()
            socketService.connect()
            socketService.authenticate(response.data.access_token)
          }
          
          return true
        }
      }
      
      return true
    } catch (err) {
      console.error('Token refresh error:', err)
      if (err.response && err.response.status === 401) {
        logout()
      }
      return false
    }
  }

  // Actions
  // 登录
  async function login(credentials) {
    loading.value = true
    error.value = null
    
    try {
      const response = await userApi.login(credentials)
      const accessToken = response.data.access_token
      
      // 存储token
      setToken(accessToken)
      
      // 解析JWT获取用户基本信息
      const base64Url = accessToken.split('.')[1]
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
      const payload = JSON.parse(window.atob(base64))
      
      const userData = {
        id: payload.sub, // JWT中的subject通常是用户ID
        exp: payload.exp,
      }
      
      // 获取用户详细信息
      try {
        const userResponse = await userApi.getUserInfo();
        if (userResponse && userResponse.data) {
          // 合并JWT中的信息和用户详情
          Object.assign(userData, {
            ...userResponse.data,
            created_at: userResponse.data.created_at || userResponse.data.joined_at
          });
        } else {
          // 如果获取用户信息失败，使用邮箱前缀作为用户名
          userData.username = credentials.email.split('@')[0];
        }
      } catch (userErr) {
        console.error('获取用户信息失败:', userErr);
        // 如果获取用户信息失败，使用邮箱前缀作为用户名
        userData.username = credentials.email.split('@')[0];
      }
      
      // 存储用户信息
      setUser(userData)
      
      // 连接WebSocket
      socketService.connect()
      socketService.authenticate(accessToken)
      
      // 设置定时器检查令牌
      startTokenRefreshTimer()
      
      return true
    } catch (err) {
      console.error('Login error:', err)
      error.value = err.response?.data?.msg || '登录失败，请检查邮箱和密码'
      return false
    } finally {
      loading.value = false
    }
  }

  // 注册
  async function register(userData) {
    loading.value = true
    error.value = null
    
    try {
      await userApi.register(userData)
      return true
    } catch (err) {
      console.error('Registration error:', err)
      error.value = err.response?.data?.msg || '注册失败，请稍后重试'
      return false
    } finally {
      loading.value = false
    }
  }

  // 刷新令牌
  async function refreshToken() {
    if (!token.value) return false
    
    try {
      const response = await userApi.refreshToken()
      if (response.data && response.data.access_token) {
        setToken(response.data.access_token)
        return true
      }
      return false
    } catch (err) {
      console.error('Token refresh failed:', err)
      if (err.response && err.response.status === 401) {
        logout()
      }
      return false
    }
  }

  // 登出
  function logout() {
    // 清除token和用户信息
    setToken('')
    setUser(null)
    
    // 清除令牌刷新定时器
    if (tokenRefreshTimer) {
      clearInterval(tokenRefreshTimer)
      tokenRefreshTimer = null
    }
    
    // 断开WebSocket连接
    socketService.disconnect()
  }

  // 检查Token是否过期
  function checkTokenExpiration() {
    if (!user.value || !user.value.exp) {
      return false
    }
    
    const now = Math.floor(Date.now() / 1000)
    if (now >= user.value.exp) {
      // Token已过期，执行登出
      logout()
      return false
    }
    
    return true
  }

  // 令牌刷新定时器
  let tokenRefreshTimer = null
  
  // 启动令牌刷新定时器
  function startTokenRefreshTimer() {
    // 清除现有定时器
    if (tokenRefreshTimer) {
      clearInterval(tokenRefreshTimer)
    }
    
    // 每分钟检查一次令牌状态
    tokenRefreshTimer = setInterval(() => {
      checkAndRefreshToken()
    }, 60000)
  }
  
  // 在组件挂载时初始化
  function initialize() {
    // 如果有令牌，设置 axios 默认请求头
    if (token.value) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
      
      // 验证令牌是否有效
      checkAndRefreshToken().then(valid => {
        if (valid) {
          // 如果令牌有效，获取最新的用户信息
          refreshUserInfo().then(() => {
            console.log('用户信息已刷新:', user.value?.username);
          });
          
          // 启动刷新定时器并连接 WebSocket
          startTokenRefreshTimer()
          
          // 连接WebSocket
          if (!socketService.connected.value) {
            socketService.connect()
            socketService.authenticate(token.value)
          }
        }
      })
    }
  }
  
  // 刷新用户信息
  async function refreshUserInfo() {
    if (!token.value) return false
    
    // 如果已经尝试过3次，则不再尝试
    if (userInfoRefreshAttempts >= 3) {
      console.log('已尝试刷新用户信息3次，不再尝试');
      return false;
    }
    
    try {
      const userResponse = await userApi.getUserInfo()
      if (userResponse && userResponse.data) {
        // 重置尝试次数
        userInfoRefreshAttempts = 0;
        
        // 保留原有的id和exp，更新其他信息
        const updatedUser = {
          ...user.value,
          ...userResponse.data,
          created_at: userResponse.data.created_at || userResponse.data.joined_at
        }
        setUser(updatedUser)
        return true
      }
      
      // 增加尝试次数
      userInfoRefreshAttempts++;
      return false
    } catch (err) {
      console.error('刷新用户信息失败:', err)
      
      // 如果是404错误，说明后端可能没有实现该接口，增加尝试次数
      if (err.response && err.response.status === 404) {
        userInfoRefreshAttempts += 3; // 直接设为3，不再尝试
      } else {
        // 其他错误，增加尝试次数
        userInfoRefreshAttempts++;
      }
      
      return false
    }
  }
  
  // 用户信息刷新尝试次数
  let userInfoRefreshAttempts = 0;
  
  // 管理员登录
  async function adminLogin(credentials) {
    loading.value = true;
    error.value = null;
    
    console.log('开始管理员登录流程:', credentials);
    
    try {
      // 调用管理员登录API
      console.log('发送管理员登录请求到:', '/api/admin/login');
      const response = await userApi.adminLogin(credentials);
      console.log('管理员登录API响应:', response.data);
      
      const accessToken = response.data.access_token;
      
      // 存储token
      setToken(accessToken);
      
      // 解析JWT获取用户基本信息
      const base64Url = accessToken.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const payload = JSON.parse(window.atob(base64));
      console.log('JWT载荷解析:', payload);
      
      const userData = {
        id: payload.sub,
        exp: payload.exp,
        role: 'admin',  // 设置角色为管理员
      };
      
      // 获取管理员详细信息
      try {
        console.log('获取管理员详细信息');
        const userResponse = await userApi.getAdminInfo();
        console.log('管理员详细信息响应:', userResponse.data);
        
        if (userResponse && userResponse.data) {
          // 合并JWT中的信息和用户详情
          Object.assign(userData, userResponse.data);
        } else {
          // 如果获取用户信息失败，使用邮箱作为用户名
          userData.username = credentials.email;
          userData.email = credentials.email;
          console.warn('未能获取管理员详细信息，使用邮箱作为用户名');
        }
      } catch (userErr) {
        console.error('获取管理员信息失败:', userErr);
        userData.username = credentials.email;
        userData.email = credentials.email;
      }
      
      console.log('最终管理员用户数据:', userData);
      
      // 存储用户信息
      setUser(userData);
      
      // 启动令牌刷新定时器
      startTokenRefreshTimer();
      
      return true;
    } catch (err) {
      console.error('管理员登录错误:', err);
      if (err.response) {
        console.error('错误响应状态:', err.response.status);
        console.error('错误响应数据:', err.response.data);
      }
      error.value = err.response?.data?.msg || '登录失败，请检查账号和密码';
      return false;
    } finally {
      loading.value = false;
    }
  }
  
  // 简化的管理员登录方法 - 使用硬编码的凭据验证
  async function adminSimpleLogin(credentials) {
    loading.value = true;
    error.value = null;
    
    console.log('开始简化管理员登录流程:', credentials);
    
    try {
      // 调用简化的管理员登录API
      console.log('发送简化管理员登录请求到:', '/api/admin/simple_login');
      const response = await userApi.adminSimpleLogin(credentials);
      console.log('简化管理员登录API响应:', response.data);
      
      const accessToken = response.data.access_token;
      
      // 存储token
      setToken(accessToken);
      
      // 创建管理员用户数据
      const userData = {
        id: response.data.user_id,
        username: 'admin',
        email: credentials.email,
        role: 'admin',  // 设置角色为管理员
        is_admin: true
      };
      
      console.log('管理员用户数据:', userData);
      
      // 存储用户信息
      setUser(userData);
      
      // 启动令牌刷新定时器
      startTokenRefreshTimer();
      
      return true;
    } catch (err) {
      console.error('简化管理员登录错误:', err);
      if (err.response) {
        console.error('错误响应状态:', err.response.status);
        console.error('错误响应数据:', err.response.data);
      }
      error.value = err.response?.data?.msg || '登录失败，请检查账号和密码';
      return false;
    } finally {
      loading.value = false;
    }
  }
  
  // 初始化
  initialize()

  return {
    // 状态
    token,
    user,
    loading,
    error,
    
    // Getters
    isAuthenticated,
    userId,
    username,
    isAdmin,
    
    // Actions
    login,
    register,
    logout,
    checkTokenExpiration,
    refreshToken,
    checkAndRefreshToken,
    refreshUserInfo,
    adminLogin,
    adminSimpleLogin,
    
    // 导出初始化方法，用于组件挂载时调用
    initialize
  }
})

// 你还可以定义其他的 store，例如商品相关的 store
// export const useItemStore = defineStore('item', () => {
//   const items = ref([]);
//   const fetchItems = async () => {
//     // ... 获取商品列表的逻辑
//   };
//   return { items, fetchItems };
// }); 