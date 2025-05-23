import axiosInstance from '@/plugins/axios';

// 使用从插件导入的axios实例
const axios = axiosInstance;

// 用户相关API
export const userApi = {
  // 用户注册
  register(userData) {
    return axios.post('/api/users/register', userData);
  },
  
  // 用户登录
  login(credentials) {
    return axios.post('/api/users/login', credentials);
  },
  
  // 刷新令牌
  refreshToken() {
    return axios.post('/api/users/refresh');
  },
  
  // 获取用户信息
  getUserInfo() {
    return axios.get('/api/users/me');
  },
  
  // 更新用户信息
  updateUserInfo(userData) {
    return axios.put('/api/users/me', userData);
  },
  
  // 更新用户头像
  updateAvatar(avatarFile) {
    const formData = new FormData();
    formData.append('avatar', avatarFile);
    
    return axios.put('/api/users/me', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  },
  
  // 更新用户信息（包含头像）
  updateUserProfile(userData, avatarFile = null) {
    // 如果没有头像文件，使用普通的JSON请求
    if (!avatarFile) {
      return this.updateUserInfo(userData);
    }
    
    // 否则使用FormData
    const formData = new FormData();
    
    // 添加用户数据
    if (userData.username) formData.append('username', userData.username);
    if (userData.bio) formData.append('bio', userData.bio);
    
    // 添加头像文件
    formData.append('avatar', avatarFile);
    
    return axios.put('/api/users/me', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  },
  
  // 修改密码
  changePassword(currentPassword, newPassword) {
    return axios.post('/api/users/change-password', {
      current_password: currentPassword,
      new_password: newPassword
    });
  },
  
  // 获取用户统计信息
  getUserStats() {
    return axios.get('/api/analytics/user-stats');
  },
  
  // 获取浏览历史
  getBrowseHistory() {
    console.log('调用getBrowseHistory API');
    return axios.get('/api/users/browse-history')
      .then(response => {
        console.log('获取浏览历史成功:', response.data);
        return response.data;
      })
      .catch(error => {
        console.error('获取浏览历史失败:', error);
        throw error;
      });
  },
  
  // 添加浏览历史
  addBrowseHistory(itemId) {
    console.log('添加浏览历史, itemId:', itemId);
    return axios.post(`/api/users/browse-history/${itemId}`)
      .then(response => {
        console.log('添加浏览历史成功:', response.data);
        return response.data;
      })
      .catch(error => {
        console.error('添加浏览历史失败:', error);
        throw error;
      });
  },
  
  // 管理员登录
  adminLogin(credentials) {
    console.log('发起管理员登录请求:', { email: credentials.email, password: '******' });
    return axios.post('/api/admin/login', credentials)
      .then(response => {
        console.log('管理员登录成功:', response.data);
        return response;
      })
      .catch(error => {
        console.error('管理员登录失败:', error);
        if (error.response) {
          console.error('服务器响应状态码:', error.response.status);
          console.error('服务器响应数据:', error.response.data);
        } else if (error.request) {
          console.error('请求已发送但未收到响应');
        } else {
          console.error('请求配置错误:', error.message);
        }
        throw error;
      });
  },
  
  // 简化的管理员登录（不使用密码哈希验证）
  adminSimpleLogin(credentials) {
    console.log('发起简化管理员登录请求:', { email: credentials.email, password: '******' });
    return axios.post('/api/admin/simple_login', credentials)
      .then(response => {
        console.log('简化管理员登录成功:', response.data);
        return response;
      })
      .catch(error => {
        console.error('简化管理员登录失败:', error);
        if (error.response) {
          console.error('服务器响应状态码:', error.response.status);
          console.error('服务器响应数据:', error.response.data);
        } else if (error.request) {
          console.error('请求已发送但未收到响应');
        } else {
          console.error('请求配置错误:', error.message);
        }
        throw error;
      });
  },
  
  // 获取管理员信息
  getAdminInfo() {
    return axios.get('/api/admin/me');
  },
  
  // 获取所有用户列表（管理员功能）
  getAllUsers(params = {}) {
    return axios.get('/api/admin/users', { params });
  },
  
  // 更新用户信息（管理员功能）
  updateUser(userId, userData) {
    return axios.put(`/api/admin/users/${userId}`, userData);
  },
  
  // 删除用户（管理员功能）
  deleteUser(userId) {
    return axios.delete(`/api/admin/users/${userId}`);
  }
};

// 商品相关API
export const itemApi = {
  // 获取商品列表
  getItems(params) {
    console.log('调用getItems API，参数:', params);
    return axios.get('/api/items', { params })
      .then(response => {
        console.log('getItems API响应:', response.data);
        return response;
      })
      .catch(error => {
        console.error('getItems API错误:', error);
        throw error;
      });
  },
  
  // 获取单个商品详情
  getItem(id) {
    return axios.get(`/api/items/${id}`);
  },
  
  // 创建新商品
  createItem(itemData) {
    // 检查是否是FormData类型
    if (itemData instanceof FormData) {
      return axios.post('/api/items', itemData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
    } else {
      // 如果是普通对象，使用JSON格式
      return axios.post('/api/items', itemData);
    }
  },
  
  // 将图片文件转换为Base64字符串
  async fileToBase64(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve(reader.result);
      reader.onerror = error => reject(error);
    });
  },
  
  // 使用Base64编码的方式创建商品（包含图片）
  async createItemWithBase64Images(itemData, imageFiles) {
    try {
      console.log('准备使用Base64方式上传商品和图片...');
      
      // 转换所有图片为Base64
      const base64Promises = Array.from(imageFiles).map(file => this.fileToBase64(file));
      const base64Images = await Promise.all(base64Promises);
      
      console.log(`已转换 ${base64Images.length} 张图片为Base64格式`);
      
      // 创建包含Base64编码图片的商品数据
      const completeItemData = {
        ...itemData,
        images: base64Images.map(base64 => ({
          data: base64,
          name: imageFiles[base64Images.indexOf(base64)].name,
          type: imageFiles[base64Images.indexOf(base64)].type
        }))
      };
      
      // 发送商品数据（JSON格式，包含Base64编码的图片）
      return this.createItem(completeItemData);
    } catch (error) {
      console.error('上传商品时出错:', error);
      throw error;
    }
  },
  
  // 更新商品
  updateItem(id, itemData) {
    return axios.put(`/api/items/${id}`, itemData);
  },
  
  // 删除商品
  deleteItem(id) {
    return axios.delete(`/api/items/${id}`);
  },
  
  // 获取用户发布的商品
  getUserItems() {
    return axios.get('/api/items/user');
  },
  
  // 获取推荐商品
  getRelatedItems(itemId) {
    return axios.get(`/api/items/${itemId}/related`);
  }
};

// 收藏相关API
export const favoriteApi = {
  // 获取收藏列表
  getFavorites() {
    console.log('调用getFavorites API');
    return axios.get('/api/users/favorites')
      .then(response => {
        console.log('获取收藏列表成功:', response.data);
        return response.data;
      })
      .catch(error => {
        console.error('获取收藏列表失败:', error);
        throw error;
      });
  },
  
  // 添加收藏
  addFavorite(itemId) {
    console.log('添加收藏, itemId:', itemId);
    return axios.post(`/api/users/favorites/${itemId}`)
      .then(response => {
        console.log('添加收藏成功:', response.data);
        return response.data;
      })
      .catch(error => {
        console.error('添加收藏失败:', error);
        throw error;
      });
  },
  
  // 移除收藏
  removeFavorite(itemId) {
    console.log('移除收藏, itemId:', itemId);
    return axios.delete(`/api/users/favorites/${itemId}`)
      .then(response => {
        console.log('移除收藏成功:', response.data);
        return response.data;
      })
      .catch(error => {
        console.error('移除收藏失败:', error);
        throw error;
      });
  },
  
  // 检查是否已收藏
  checkIsFavorite(itemId) {
    return axios.get(`/api/users/favorites/${itemId}/check`);
  }
};

// 消息相关API
export const messageApi = {
  // 获取联系人列表
  getContacts() {
    return axios.get('/api/messages/contacts');
  },
  
  // 获取与特定用户的聊天记录
  getMessages(userId) {
    console.log('获取与用户的聊天记录, userId:', userId);
    return axios.get(`/api/messages/${userId}`)
      .then(response => {
        console.log('获取聊天记录成功:', response.data);
        return response.data;
      })
      .catch(error => {
        console.error('获取聊天记录失败:', error);
        // 如果是网络错误，提供更友好的错误信息
        if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
          throw new Error('网络连接超时，请检查您的网络连接');
        } else if (!error.response) {
          throw new Error('网络连接错误，请稍后重试');
        }
        throw error;
      });
  },
  
  // 发送消息
  sendMessage(messageData) {
    console.log('发送消息:', messageData);
    return axios.post('/api/messages/send', messageData)
      .then(response => {
        console.log('消息发送成功:', response.data);
        return response.data;
      })
      .catch(error => {
        console.error('消息发送失败:', error);
        // 如果是网络错误，提供更友好的错误信息
        if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
          throw new Error('网络连接超时，请检查您的网络连接');
        } else if (!error.response) {
          throw new Error('网络连接错误，请稍后重试');
        }
        throw error;
      });
  },
  
  // 标记消息为已读
  markAsRead(messageId) {
    return axios.put(`/api/messages/${messageId}/read`);
  },
  
  // 获取未读消息数量
  getUnreadCount() {
    return axios.get('/api/messages/unread/count');
  },
  
  // 标记与某用户的所有消息为已读
  markAllAsRead(userId) {
    return axios.put(`/api/messages/read-all/${userId}`);
  }
};

// 统计相关API
export const analyticsApi = {
  // 获取用户统计
  getUserStats() {
    return axios.get('/api/analytics/user-stats')
      .then(response => {
        console.log('获取用户统计信息成功:', response.data);
        return response.data;
      })
      .catch(error => {
        console.error('获取用户统计信息失败:', error);
        throw error;
      });
  },
  
  // 记录商品浏览
  recordItemView(itemId) {
    return axios.post(`/api/analytics/item-view/${itemId}`);
  },
  
  // 获取热门商品
  getPopularItems() {
    return axios.get('/api/analytics/popular-items');
  }
};

// 商品辅助函数 - 新增的简化API
export const itemHelpers = {
  // 加载商品列表 - 简化版
  async loadItems(params = {}, signal = null) {
    try {
      const config = { params };
      
      // 如果提供了中止信号，添加到请求配置中
      if (signal) {
        config.signal = signal;
      }
      
      const response = await axios.get('/api/items', config);
      console.log('商品列表原始响应:', response);
      
      // 尝试标准化响应格式
      if (response.data && typeof response.data === 'object') {
        // 可能是 { items: [...], total: n } 格式
        return {
          items: Array.isArray(response.data.items) ? response.data.items : 
                (Array.isArray(response.data) ? response.data : []),
          total: response.data.total || 0
        };
      } else if (Array.isArray(response.data)) {
        // 直接是数组
        return {
          items: response.data,
          total: response.data.length
        };
      } else {
        // 直接返回原始响应
        return response.data;
      }
    } catch (error) {
      console.error('加载商品列表失败:', error);
      // 重新抛出错误，让调用者处理
      throw error;
    }
  },
  
  // 加载用户发布的商品
  async loadUserItems(userId) {
    try {
      // 使用专门的API获取当前用户的商品
      const response = await itemApi.getUserItems();
      console.log('获取用户商品响应:', response);
      
      if (response.data && typeof response.data === 'object') {
        // 标准化响应格式
        return {
          items: Array.isArray(response.data.items) ? response.data.items : 
                (Array.isArray(response.data) ? response.data : []),
          total: response.data.total || 0
        };
      } else {
        return { items: [], total: 0 };
      }
    } catch (error) {
      console.error('加载用户商品失败:', error);
      return { items: [], total: 0 };
    }
  },
  
  // 使用本地文件路径发布商品（新方法）
  async publishItemWithLocalImages(itemData, imageFiles = []) {
    try {
      // 如果有图片文件，先将其保存到本地目录
      if (imageFiles && imageFiles.length > 0) {
        // 生成唯一的文件名前缀（基于时间戳和随机数）
        const filePrefix = `${Date.now()}_${Math.floor(Math.random() * 1000)}`;
        
        // 本地图片路径数组
        const imagePaths = [];
        
        // 处理每个图片文件
        for (let i = 0; i < imageFiles.length; i++) {
          const file = imageFiles[i];
          
          // 创建唯一文件名
          const fileName = `${filePrefix}_${i}_${file.name.replace(/[^a-zA-Z0-9.]/g, '_')}`;
          
          // 这里仅构建相对路径，实际文件保存由浏览器进行
          const filePath = `/images/items/${fileName}`;
          
          // 将路径添加到数组
          imagePaths.push({
            url: filePath,
            name: file.name,
            type: file.type
          });
          
          // 在实际应用中，这里需要通过文件API将文件保存到本地
          // 在浏览器环境中我们无法直接写入文件系统，通常需要单独的文件上传API
          console.log(`模拟保存图片: ${filePath}`);
        }
        
        // 添加图片路径到商品数据
        itemData.images = imagePaths;
      }
      
      // 发送数据（不含实际图片内容，只包含路径）
      console.log('发送不含图片内容的商品数据:', itemData);
      const response = await axios.post('/api/items', itemData);
      return response.data;
    } catch (error) {
      console.error('发布商品失败:', error);
      throw error;
    }
  },
  
  // 发布新商品，不再使用Base64编码图片
  async publishItem(itemData, imageFiles = []) {
    // 改为使用本地图片路径的方法
    return this.publishItemWithLocalImages(itemData, imageFiles);
  },
  
  // 获取图片URL（用于显示）
  getImageUrl(item) {
    if (!item || !item.images) return '/placeholder.jpg';
    
    // 服务器基础URL
    const baseUrl = import.meta.env.VITE_API_BASE_URL || '';
    
    // 处理图片数组或单个图片对象
    if (Array.isArray(item.images)) {
      if (item.images.length === 0) return '/placeholder.jpg';
      const img = item.images[0];
      
      // 如果是字符串路径
      if (typeof img === 'string') {
        // 如果是以/static开头的服务器路径
        if (img.startsWith('/static')) {
          return `${baseUrl}${img}`;
        }
        // 如果是完整URL或Base64
        if (img.startsWith('http') || img.startsWith('data:')) {
          return img;
        }
        return img;
      }
      
      // 如果是对象
      if (img && typeof img === 'object') {
        // 检查是否有路径属性
        if (img.path && img.path.startsWith('/static')) {
          return `${baseUrl}${img.path}`;
        }
        return img.url || img.data || img.path || '/placeholder.jpg';
      }
    } else if (typeof item.images === 'string') {
      // 单个字符串路径
      if (item.images.startsWith('/static')) {
        return `${baseUrl}${item.images}`;
      }
      if (item.images.startsWith('http') || item.images.startsWith('data:')) {
        return item.images;
      }
      return item.images;
    } else if (item.images && typeof item.images === 'object') {
      // 单个对象
      if (item.images.path && item.images.path.startsWith('/static')) {
        return `${baseUrl}${item.images.path}`;
      }
      return item.images.url || item.images.data || item.images.path || '/placeholder.jpg';
    }
    
    return '/placeholder.jpg';
  },
  
  // 文件转Base64
  fileToBase64(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve(reader.result);
      reader.onerror = error => reject(error);
    });
  }
};

// 辅助函数，用于统一处理错误
export const handleApiError = (error, customMessage = null) => {
  console.error('API Error:', error);
  // 可以在这里添加额外的错误处理逻辑
  
  if (customMessage) {
    console.error(customMessage);
  }
  
  return error.response?.data?.msg || 'An error occurred';
};

// 管理员相关API
export const adminApi = {
  // 获取管理员统计信息
  getDashboardStats() {
    return axios.get('/api/admin/stats');
  },
  
  // 获取所有用户
  getUsers(params = {}) {
    return axios.get('/api/admin/users', { params });
  },
  
  // 获取单个用户详情
  getUser(userId) {
    return axios.get(`/api/admin/users/${userId}`);
  },
  
  // 更新用户
  updateUser(userId, userData) {
    return axios.put(`/api/admin/users/${userId}`, userData);
  },
  
  // 删除用户
  deleteUser(userId) {
    return axios.delete(`/api/admin/users/${userId}`);
  },
  
  // 获取所有商品
  getItems(params = {}) {
    return axios.get('/api/admin/items', { params });
  },
  
  // 获取单个商品详情
  getItem(itemId) {
    return axios.get(`/api/admin/items/${itemId}`);
  },
  
  // 更新商品
  updateItem(itemId, itemData) {
    return axios.put(`/api/admin/items/${itemId}`, itemData);
  },
  
  // 删除商品
  deleteItem(itemId) {
    return axios.delete(`/api/admin/items/${itemId}`);
  },
  
  // 获取系统日志
  getLogs(params = {}) {
    return axios.get('/api/admin/logs', { params });
  },
  
  // 获取所有消息
  getMessages(params = {}) {
    console.log('获取消息列表, 参数:', params);
    return axios.get('/api/admin/messages', { params })
      .then(response => {
        console.log('获取消息列表成功:', response.data);
        return response.data;
      })
      .catch(error => {
        console.error('获取消息列表失败:', error);
        throw error;
      });
  },
  
  // 获取单条消息详情
  getMessage(messageId) {
    return axios.get(`/api/admin/messages/${messageId}`)
      .then(response => {
        console.log('获取消息详情成功:', response.data);
        return response.data;
      })
      .catch(error => {
        console.error('获取消息详情失败:', error);
        throw error;
      });
  },
  
  // 标记消息为已读
  markMessageAsRead(messageId) {
    return axios.put(`/api/admin/messages/${messageId}/read`)
      .then(response => {
        console.log('标记消息为已读成功:', response.data);
        return response.data;
      })
      .catch(error => {
        console.error('标记消息为已读失败:', error);
        throw error;
      });
  },
  
  // 删除单条消息
  deleteMessage(messageId) {
    return axios.delete(`/api/admin/messages/${messageId}`)
      .then(response => {
        console.log('删除消息成功:', response.data);
        return response.data;
      })
      .catch(error => {
        console.error('删除消息失败:', error);
        throw error;
      });
  },
  
  // 批量删除消息
  batchDeleteMessages(messageIds) {
    return axios.post('/api/admin/messages/batch-delete', { message_ids: messageIds })
      .then(response => {
        console.log('批量删除消息成功:', response.data);
        return response.data;
      })
      .catch(error => {
        console.error('批量删除消息失败:', error);
        throw error;
      });
  }
};

// 默认导出所有API
export default {
  user: userApi,
  item: itemApi,
  favorite: favoriteApi,
  message: messageApi,
  analytics: analyticsApi,
  handleError: handleApiError
}; 