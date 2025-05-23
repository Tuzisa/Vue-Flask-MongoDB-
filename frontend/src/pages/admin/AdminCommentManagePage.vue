<template>
  <div class="admin-comment-manage">
    <h2>评论管理</h2>
    
    <div class="search-bar">
      <el-input
        v-model="searchQuery"
        placeholder="搜索评论内容"
        clearable
        @clear="loadComments"
      >
        <template #append>
          <el-button @click="loadComments">
            <el-icon><Search /></el-icon>
          </el-button>
        </template>
      </el-input>
    </div>
    
    <el-table
      :data="comments"
      style="width: 100%"
      v-loading="loading"
      border
    >
      <el-table-column prop="username" label="用户" width="120" />
      <el-table-column prop="product_title" label="商品" width="200" />
      <el-table-column prop="content" label="评论内容" min-width="300">
        <template #default="scope">
          <span :class="{ 'deleted-comment': scope.row.is_deleted }">
            {{ scope.row.is_deleted ? '该评论已被用户删除' : scope.row.content }}
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="评论时间" width="180">
        <template #default="scope">
          {{ formatDate(scope.row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="类型" width="100">
        <template #default="scope">
          {{ scope.row.parent_id ? '回复' : '主评论' }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120">
        <template #default="scope">
          <el-button 
            type="danger" 
            size="small" 
            @click="confirmDeleteComment(scope.row)"
          >删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <el-pagination
      v-if="total > 0"
      :current-page="currentPage"
      :page-size="pageSize"
      :total="total"
      layout="total, prev, pager, next"
      @current-change="handlePageChange"
      class="pagination"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Search } from '@element-plus/icons-vue';
import axios from 'axios';

// 状态
const comments = ref([]);
const total = ref(0);
const currentPage = ref(1);
const pageSize = ref(10);
const loading = ref(false);
const searchQuery = ref('');

// 初始化
onMounted(() => {
  loadComments();
});

// 加载评论列表
const loadComments = async () => {
  loading.value = true;
  try {
    const response = await axios.get('/api/admin/comments', {
      params: {
        page: currentPage.value,
        per_page: pageSize.value,
        query: searchQuery.value
      }
    });
    
    comments.value = response.data.comments;
    total.value = response.data.total;
  } catch (error) {
    console.error('加载评论列表失败:', error);
    ElMessage.error('加载评论列表失败');
  } finally {
    loading.value = false;
  }
};

// 确认删除评论
const confirmDeleteComment = async (comment) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这条评论吗？此操作不可恢复！', 
      '警告', 
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    );
    
    await axios.delete(`/api/admin/comments/${comment._id}`);
    ElMessage.success('评论已删除');
    loadComments(); // 重新加载评论列表
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除评论失败:', error);
      ElMessage.error('删除评论失败');
    }
  }
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
</script>

<style scoped>
.admin-comment-manage {
  padding: 20px;
}

.search-bar {
  margin-bottom: 20px;
  max-width: 400px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.deleted-comment {
  color: #999;
  font-style: italic;
}

.el-table {
  margin-top: 20px;
}
</style> 