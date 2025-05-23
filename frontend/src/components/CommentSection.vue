<template>
  <div class="comment-section">
    <h3 class="comment-section-title">商品评论</h3>
    
    <!-- 评论输入框 -->
    <div class="comment-input-box" v-if="isAuthenticated">
      <el-input
        v-model="newComment"
        type="textarea"
        :rows="3"
        placeholder="写下你的评论..."
        :maxlength="500"
        show-word-limit
      />
      <el-button 
        type="primary" 
        @click="submitComment" 
        :loading="submitting"
        :disabled="!newComment.trim()"
      >发表评论</el-button>
    </div>
    <div v-else class="login-prompt">
      <p>请<el-button type="text" @click="$router.push('/login')">登录</el-button>后发表评论</p>
    </div>

    <!-- 评论列表 -->
    <div class="comments-list" v-loading="loading">
      <template v-if="comments.length > 0">
        <div v-for="comment in comments" :key="comment._id" class="comment-item">
          <!-- 主评论 -->
          <div class="comment-main">
            <el-avatar :size="40" :src="comment.avatar || '/images/moren.jpg'" />
            <div class="comment-content">
              <div class="comment-header">
                <span class="username">{{ comment.username }}</span>
                <span class="time">{{ formatDate(comment.created_at) }}</span>
              </div>
              <p class="comment-text" :class="{ 'deleted': comment.is_deleted }">
                {{ comment.is_deleted ? '该评论已被用户删除' : comment.content }}
              </p>
              <div class="comment-actions">
                <el-button 
                  type="text" 
                  @click="showReplyInput(comment._id)"
                  v-if="isAuthenticated && !comment.is_deleted"
                >回复</el-button>
                <el-button 
                  type="text" 
                  class="delete-btn"
                  @click="deleteComment(comment._id)"
                  v-if="canDelete(comment) && !comment.is_deleted"
                >删除</el-button>
              </div>
              
              <!-- 回复输入框 -->
              <div class="reply-input" v-if="replyToId === comment._id">
                <el-input
                  v-model="replyContent"
                  type="textarea"
                  :rows="2"
                  placeholder="回复评论..."
                  :maxlength="200"
                  show-word-limit
                />
                <div class="reply-actions">
                  <el-button size="small" @click="cancelReply">取消</el-button>
                  <el-button 
                    type="primary" 
                    size="small" 
                    @click="submitReply(comment._id)"
                    :disabled="!replyContent.trim()"
                  >回复</el-button>
                </div>
              </div>
            </div>
          </div>

          <!-- 回复列表 -->
          <div class="replies-list" v-if="comment.replies && comment.replies.length > 0">
            <div v-for="reply in comment.replies" :key="reply._id" class="reply-item">
              <el-avatar :size="32" :src="reply.avatar || '/images/moren.jpg'" />
              <div class="reply-content">
                <div class="reply-header">
                  <span class="username">{{ reply.username }}</span>
                  <span class="time">{{ formatDate(reply.created_at) }}</span>
                </div>
                <p class="reply-text" :class="{ 'deleted': reply.is_deleted }">
                  {{ reply.is_deleted ? '该评论已被用户删除' : reply.content }}
                </p>
                <div class="reply-actions" v-if="canDelete(reply) && !reply.is_deleted">
                  <el-button 
                    type="text" 
                    class="delete-btn"
                    @click="deleteComment(reply._id)"
                  >删除</el-button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
      <el-empty v-else-if="!loading" description="暂无评论" />
    </div>

    <!-- 分页 -->
    <div class="pagination" v-if="total > perPage">
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="perPage"
        :total="total"
        layout="prev, pager, next"
        @current-change="handlePageChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { ElMessage, ElMessageBox } from 'element-plus';
import axios from 'axios';

const props = defineProps({
  productId: {
    type: String,
    required: true
  }
});

const authStore = useAuthStore();
const isAuthenticated = computed(() => authStore.isAuthenticated);

// 状态
const comments = ref([]);
const loading = ref(false);
const submitting = ref(false);
const newComment = ref('');
const replyContent = ref('');
const replyToId = ref(null);
const currentPage = ref(1);
const perPage = ref(10);
const total = ref(0);

// 加载评论
const loadComments = async () => {
  loading.value = true;
  try {
    const response = await axios.get(`/api/products/${props.productId}/comments`, {
      params: {
        page: currentPage.value,
        per_page: perPage.value
      }
    });
    comments.value = response.data.comments;
    total.value = response.data.total;
  } catch (error) {
    console.error('加载评论失败:', error);
    ElMessage.error('加载评论失败');
  } finally {
    loading.value = false;
  }
};

// 提交评论
const submitComment = async () => {
  if (!newComment.value.trim()) return;
  
  submitting.value = true;
  try {
    await axios.post(`/api/products/${props.productId}/comments`, {
      content: newComment.value
    });
    
    ElMessage.success('评论发表成功');
    newComment.value = '';
    loadComments(); // 重新加载评论列表
  } catch (error) {
    console.error('发表评论失败:', error);
    ElMessage.error('发表评论失败');
  } finally {
    submitting.value = false;
  }
};

// 显示回复输入框
const showReplyInput = (commentId) => {
  replyToId.value = commentId;
  replyContent.value = '';
};

// 取消回复
const cancelReply = () => {
  replyToId.value = null;
  replyContent.value = '';
};

// 提交回复
const submitReply = async (parentId) => {
  if (!replyContent.value.trim()) return;
  
  submitting.value = true;
  try {
    await axios.post(`/api/products/${props.productId}/comments`, {
      content: replyContent.value,
      parent_id: parentId
    });
    
    ElMessage.success('回复发表成功');
    cancelReply();
    loadComments(); // 重新加载评论列表
  } catch (error) {
    console.error('发表回复失败:', error);
    ElMessage.error('发表回复失败');
  } finally {
    submitting.value = false;
  }
};

// 删除评论
const deleteComment = async (commentId) => {
  try {
    await ElMessageBox.confirm('确定要删除这条评论吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    });
    
    await axios.delete(`/api/comments/${commentId}`);
    ElMessage.success('评论已删除');
    loadComments(); // 重新加载评论列表
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除评论失败:', error);
      ElMessage.error('删除评论失败');
    }
  }
};

// 检查是否可以删除评论
const canDelete = (comment) => {
  return isAuthenticated.value && comment.user_id === authStore.userId;
};

// 处理分页变化
const handlePageChange = (page) => {
  currentPage.value = page;
  loadComments();
};

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

// 监听商品ID变化
watch(() => props.productId, () => {
  currentPage.value = 1;
  loadComments();
});

// 组件挂载时加载评论
onMounted(() => {
  loadComments();
});
</script>

<style scoped>
.comment-section {
  margin-top: 30px;
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
}

.comment-section-title {
  margin-bottom: 20px;
  font-size: 18px;
  font-weight: 600;
}

.comment-input-box {
  margin-bottom: 30px;
}

.comment-input-box .el-button {
  margin-top: 10px;
}

.login-prompt {
  text-align: center;
  padding: 20px;
  color: #666;
}

.comments-list {
  margin-top: 20px;
}

.comment-item {
  margin-bottom: 30px;
}

.comment-main {
  display: flex;
  gap: 15px;
}

.comment-content {
  flex: 1;
}

.comment-header {
  margin-bottom: 8px;
}

.username {
  font-weight: 500;
  margin-right: 10px;
}

.time {
  color: #999;
  font-size: 12px;
}

.comment-text {
  margin: 0;
  line-height: 1.6;
}

.comment-text.deleted {
  color: #999;
  font-style: italic;
}

.comment-actions {
  margin-top: 8px;
}

.delete-btn {
  color: #ff4d4f;
}

.reply-input {
  margin-top: 15px;
}

.reply-actions {
  margin-top: 10px;
  text-align: right;
}

.replies-list {
  margin-left: 55px;
  margin-top: 15px;
}

.reply-item {
  display: flex;
  gap: 12px;
  margin-bottom: 15px;
  padding: 12px;
  background-color: #f8f9fa;
  border-radius: 6px;
}

.reply-content {
  flex: 1;
}

.reply-header {
  margin-bottom: 6px;
}

.reply-text {
  margin: 0;
  font-size: 14px;
  line-height: 1.5;
}

.reply-text.deleted {
  color: #999;
  font-style: italic;
}

.pagination {
  margin-top: 20px;
  text-align: center;
}
</style> 