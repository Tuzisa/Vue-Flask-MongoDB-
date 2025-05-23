import { ref } from 'vue';
import { useAuthStore } from '@/stores/auth';

class WebSocketService {
  constructor() {
    this.ws = null;
    this.connected = ref(false);
    this.messageHandlers = new Set();
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000;
  }

  connect() {
    const authStore = useAuthStore();
    if (!authStore.isAuthenticated) return;

    const baseUrl = import.meta.env.VITE_API_BASE_URL || '';
    const wsUrl = baseUrl.replace(/^http/, 'ws');
    // this.ws = new WebSocket(`${wsUrl}/api/ws/chat/${authStore.userId}`); // 移除聊天相关的 WebSocket 端点
    // 由于聊天功能已移除，这里的 WebSocket 连接需要重新考虑其用途或完全移除。
    // 暂时将其注释掉，如果项目中还有其他地方使用 WebSocket，需要调整此处的连接逻辑。
    console.warn('Chat-related WebSocket endpoint has been removed. Review WebSocket connection logic.');

    if (this.ws) { // 仅在 ws 实例实际创建后才设置事件处理器
      this.ws.onopen = () => {
        console.log('WebSocket连接已建立');
        this.connected.value = true;
        this.reconnectAttempts = 0;
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.messageHandlers.forEach(handler => handler(data));
        } catch (error) {
          console.error('处理WebSocket消息时出错:', error);
        }
      };

      this.ws.onclose = () => {
        console.log('WebSocket连接已关闭');
        this.connected.value = false;
        this.attemptReconnect();
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket错误:', error);
        this.connected.value = false;
      };
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
      this.connected.value = false;
    }
  }

  attemptReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log('达到最大重连次数，停止重连');
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
    console.log(`将在 ${delay}ms 后尝试重连...`);

    setTimeout(() => {
      console.log(`尝试重连 (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      this.connect();
    }, delay);
  }

  sendMessage(roomId, content, msgType = 'text', metadata = {}) {
    if (!this.connected.value || !this.ws) { // 增加对 this.ws 的检查
      // throw new Error('WebSocket未连接'); // 暂时注释错误抛出，因为 ws 可能未初始化
      console.warn('WebSocket not connected or initialized. Cannot send message.');
      return;
    }

    const message = {
      type: 'message',
      room_id: roomId,
      content: content,
      msg_type: msgType,
      metadata: metadata
    };

    this.ws.send(JSON.stringify(message));
  }

  onMessage(handler) {
    this.messageHandlers.add(handler);
    return () => {
      this.messageHandlers.delete(handler);
    };
  }
}

export default new WebSocketService(); 