import { io } from 'socket.io-client';
import { ref } from 'vue';

class SocketService {
  constructor() {
    this.socket = null;
    this.connected = ref(false);
    this.authenticated = ref(false);
    this.connectionError = ref(null);
    this.userId = ref(null);
    this.username = ref(null);
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.token = null;
    this.reconnectionTimer = null;
  }

  // 初始化Socket连接
  init() {
    if (this.socket) {
      return; // 如果已经初始化，不再重复初始化
    }

    // 在开发环境中，使用相对路径，这样会通过 Vite 代理
    const socketURL = window.location.origin; // 使用当前域名
    console.log('Socket.IO connecting to:', socketURL);

    // 创建连接配置对象
    const socketOptions = {
      path: '/socket.io', // Socket.IO服务器路径
      autoConnect: false, // 不自动连接，等待用户登录后再连接
      reconnection: true, // 启用重连
      reconnectionAttempts: this.maxReconnectAttempts, // 重连尝试次数
      reconnectionDelay: 1000, // 重连延迟（毫秒）
      timeout: 15000, // 增加连接超时时间
      transports: ['polling', 'websocket'], // 先尝试长轮询，然后尝试websocket
      forceNew: true, // 强制创建新的连接
      query: { from: 'frontend-app' } // 添加查询参数，方便后端区分连接来源
    };

    console.log('Initializing Socket.IO with options:', socketOptions);

    // 使用当前域名连接，通过 Vite 代理转发请求
    this.socket = io(socketURL, socketOptions);

    // 设置Socket.IO事件监听器
    this.setEventListeners();
  }

  // 设置事件监听器
  setEventListeners() {
    this.socket.on('connect', () => {
      console.log('Socket.IO connected, socket id:', this.socket.id);
      this.connected.value = true;
      this.connectionError.value = null;
      this.reconnectAttempts = 0;
      
      // 如果有保存的token，自动重新认证
      if (this.token) {
        this.authenticate(this.token);
      }
    });

    this.socket.on('connect_response', (data) => {
      console.log('Socket.IO connect response:', data);
    });

    this.socket.on('disconnect', (reason) => {
      console.log('Socket.IO disconnected:', reason);
      this.connected.value = false;
      this.authenticated.value = false;
      
      // 某些断开原因需要手动重连
      if (reason === 'io server disconnect' || reason === 'transport close') {
        this.reconnect();
      }
    });

    this.socket.on('connect_error', (error) => {
      console.error('Socket.IO connection error:', error);
      this.connectionError.value = error.message;
      this.connected.value = false;
      
      // 如果连接错误超过最大尝试次数，停止尝试
      if (++this.reconnectAttempts > this.maxReconnectAttempts) {
        console.log(`Maximum reconnection attempts (${this.maxReconnectAttempts}) reached. Giving up.`);
        this.socket.disconnect();
        return;
      }
      
      // 使用指数退避算法增加重连延迟
      const delay = Math.min(1000 * Math.pow(1.5, this.reconnectAttempts), 10000);
      
      console.log(`Attempting to reconnect in ${delay}ms... (Attempt ${this.reconnectAttempts} of ${this.maxReconnectAttempts})`);
      
      // 清除可能存在的重连定时器
      if (this.reconnectionTimer) {
        clearTimeout(this.reconnectionTimer);
      }
      
      // 设置新的重连定时器
      this.reconnectionTimer = setTimeout(() => {
        this.reconnect();
      }, delay);
    });

    this.socket.on('authenticated', (data) => {
      console.log('Socket.IO authenticated:', data);
      this.authenticated.value = true;
      this.userId.value = data.user_id;
      this.username.value = data.username;
    });

    this.socket.on('authentication_error', (data) => {
      console.error('Socket.IO authentication error:', data);
      this.authenticated.value = false;
      this.connectionError.value = data.message || 'Authentication failed';
    });

    this.socket.on('error', (data) => {
      console.error('Socket.IO error:', data);
      this.connectionError.value = data.message || 'Unknown socket error';
    });
  }

  // 连接到Socket.IO服务器
  connect() {
    if (!this.socket) {
      this.init();
    }
    
    // 如果已经连接，则不再尝试连接
    if (this.socket.connected) {
      console.log('Socket already connected');
      return;
    }
    
    console.log('Connecting to Socket.IO server...');
    this.socket.connect();
  }

  // 手动重连
  reconnect() {
    if (this.socket) {
      // 先断开现有连接
      if (this.socket.connected) {
        this.socket.disconnect();
      }
      
      // 重置Socket实例
      this.socket.close();
      this.socket = null;
      
      // 重新初始化
      this.init();
      
      // 连接
      this.socket.connect();
    }
  }

  // 使用JWT认证
  authenticate(token) {
    if (!token) {
      console.error('No token provided for authentication');
      return;
    }
    
    // 保存token以备重连使用
    this.token = token;
    
    if (!this.connected.value) {
      console.log('Socket not connected. Connecting first...');
      this.connect();
      
      // 连接后会通过connect事件处理器自动认证
      return;
    }
    
    console.log('Authenticating socket connection...');
    this.socket.emit('authenticate', { token });
  }

  // 断开连接
  disconnect() {
    if (this.socket) {
      console.log('Manually disconnecting socket...');
      
      // 清除认证信息
      this.token = null;
      this.authenticated.value = false;
      
      // 清除重连定时器
      if (this.reconnectionTimer) {
        clearTimeout(this.reconnectionTimer);
        this.reconnectionTimer = null;
      }
      
      this.socket.disconnect();
    }
  }

  // 重置连接状态
  resetConnection() {
    this.disconnect();
    this.reconnectAttempts = 0;
    this.connectionError.value = null;
    
    // 等待短暂时间后重新连接
    setTimeout(() => {
      if (this.token) {
        this.connect();
      }
    }, 1000);
  }

  // 发送消息
  sendMessage(senderId, receiverId, content, itemId = null) {
    if (!this.socket || !this.connected.value || !this.authenticated.value) {
      console.error('Cannot send message: Socket not connected or authenticated');
      return false;
    }
    
    const messageData = {
      sender_id: senderId,
      receiver_id: receiverId,
      content: content
    };

    if (itemId) {
      messageData.item_id = itemId;
    }

    this.socket.emit('send_message', messageData);
    return true;
  }

  // 通知正在输入
  notifyTyping(senderId, receiverId) {
    if (!this.socket || !this.connected.value || !this.authenticated.value) {
      return false;
    }
    
    this.socket.emit('typing', {
      sender_id: senderId,
      receiver_id: receiverId
    });
    return true;
  }

  // 标记消息为已读
  markMessageAsRead(messageId) {
    if (!this.socket || !this.connected.value || !this.authenticated.value) {
      return false;
    }
    
    this.socket.emit('mark_read', { message_id: messageId });
    return true;
  }

  // 订阅新消息事件
  onNewMessage(callback) {
    this.socket.on('new_message', callback);
    return () => this.socket.off('new_message', callback);
  }

  // 订阅消息已发送事件
  onMessageSent(callback) {
    this.socket.on('message_sent', callback);
    return () => this.socket.off('message_sent', callback);
  }

  // 订阅消息已读事件
  onMessageRead(callback) {
    this.socket.on('message_read', callback);
    return () => this.socket.off('message_read', callback);
  }

  // 订阅用户正在输入事件
  onUserTyping(callback) {
    this.socket.on('user_typing', callback);
    return () => this.socket.off('user_typing', callback);
  }
  
  // 获取连接状态
  getConnectionStatus() {
    return {
      connected: this.connected.value,
      authenticated: this.authenticated.value,
      error: this.connectionError.value,
      reconnectAttempts: this.reconnectAttempts
    };
  }
}

// 导出一个单例
export default new SocketService(); 