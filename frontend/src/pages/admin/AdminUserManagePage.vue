<template>
  <div class="admin-user-manage">
    <h2>用户管理</h2>
    
    <div class="search-bar">
      <el-input
        v-model="searchQuery"
        placeholder="搜索用户名或邮箱"
        clearable
        @clear="loadUsers"
      >
        <template #append>
          <el-button @click="loadUsers">
            <el-icon><Search /></el-icon>
          </el-button>
        </template>
      </el-input>
    </div>
    
    <el-table
      :data="users"
      style="width: 100%"
      v-loading="loading"
      border
    >
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="username" label="用户名" width="150" />
      <el-table-column prop="email" label="邮箱" width="200" />
      <el-table-column prop="created_at" label="注册时间" width="180">
        <template #default="scope">
          {{ formatDate(scope.row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作">
        <template #default="scope">
          <el-button 
            type="primary" 
            size="small" 
            @click="editUser(scope.row)"
          >编辑</el-button>
          <el-button 
            type="danger" 
            size="small" 
            @click="confirmDeleteUser(scope.row)"
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
    
    <!-- 编辑用户对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑用户信息"
      width="500px"
    >
      <el-form
        ref="editFormRef"
        :model="editForm"
        :rules="editRules"
        label-width="80px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="editForm.username" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="editForm.email" />
        </el-form-item>
        <el-form-item label="新密码" prop="password">
          <el-input v-model="editForm.password" type="password" show-password placeholder="留空表示不修改" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveUser" :loading="saving">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Search } from '@element-plus/icons-vue';
import { adminApi } from '@/services/api';

// 状态
const users = ref([]);
const total = ref(0);
const currentPage = ref(1);
const pageSize = ref(10);
const loading = ref(false);
const searchQuery = ref('');

// 编辑用户相关
const editDialogVisible = ref(false);
const editFormRef = ref(null);
const editForm = reactive({
  id: '',
  username: '',
  email: '',
  password: ''
});
const editRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ]
};
const saving = ref(false);

// 初始化
onMounted(() => {
  loadUsers();
});

// 加载用户列表
const loadUsers = async () => {
  loading.value = true;
  
  try {
    // 调用API获取用户列表
    const params = {
      page: currentPage.value,
      per_page: pageSize.value,
      query: searchQuery.value || undefined
    };
    
    console.log('请求用户列表参数:', params);
    const response = await adminApi.getUsers(params);
    console.log('用户列表响应:', response);
    
    if (response && response.data) {
      // 适应后端返回的数据结构
      if (Array.isArray(response.data)) {
        // 如果直接返回数组
        users.value = response.data;
        total.value = response.data.length;
      } else if (response.data.users) {
        // 如果返回分页对象
        users.value = response.data.users;
        total.value = response.data.total || response.data.users.length;
      } else {
        users.value = [];
        total.value = 0;
      }
      
      console.log('处理后的用户数据:', users.value);
    } else {
      users.value = [];
      total.value = 0;
    }
  } catch (error) {
    console.error('加载用户列表失败:', error);
    if (error.response) {
      console.error('错误响应:', error.response.status, error.response.data);
    }
    ElMessage.error('加载用户列表失败，请稍后重试');
    users.value = [];
    total.value = 0;
  } finally {
    loading.value = false;
  }
};

// 处理页码变化
const handlePageChange = (page) => {
  currentPage.value = page;
  loadUsers();
};

// 编辑用户
const editUser = (user) => {
  console.log('编辑用户:', user);
  editForm.id = user.id || user._id; // 适应MongoDB的_id字段
  editForm.username = user.username;
  editForm.email = user.email;
  editForm.password = '';
  editDialogVisible.value = true;
};

// 保存用户
const saveUser = async () => {
  if (!editFormRef.value) return;
  
  await editFormRef.value.validate(async (valid) => {
    if (!valid) return;
    
    saving.value = true;
    
    try {
      // 调用API保存用户信息
      const userData = {
        username: editForm.username,
        email: editForm.email
      };
      
      // 如果设置了新密码，则添加到请求数据中
      if (editForm.password) {
        userData.password = editForm.password;
      }
      
      console.log('保存用户数据:', userData);
      await adminApi.updateUser(editForm.id, userData);
      
      ElMessage.success('用户信息已更新');
      editDialogVisible.value = false;
      
      // 重新加载用户列表
      loadUsers();
    } catch (error) {
      console.error('保存用户信息失败:', error);
      if (error.response) {
        console.error('错误响应:', error.response.status, error.response.data);
      }
      ElMessage.error('保存用户信息失败，请稍后重试');
    } finally {
      saving.value = false;
    }
  });
};

// 确认删除用户
const confirmDeleteUser = (user) => {
  ElMessageBox.confirm(`确定要删除用户 ${user.username} 吗？`, '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    deleteUser(user.id || user._id); // 适应MongoDB的_id字段
  }).catch(() => {});
};

// 删除用户
const deleteUser = async (userId) => {
  loading.value = true;
  
  try {
    console.log('删除用户ID:', userId);
    // 调用API删除用户
    await adminApi.deleteUser(userId);
    
    ElMessage.success('用户已删除');
    
    // 重新加载用户列表
    loadUsers();
  } catch (error) {
    console.error('删除用户失败:', error);
    if (error.response) {
      console.error('错误响应:', error.response.status, error.response.data);
    }
    ElMessage.error('删除用户失败，请稍后重试');
    loading.value = false;
  }
};

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '';
  try {
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch (e) {
    console.error('日期格式化错误:', e);
    return dateString;
  }
};
</script>

<style scoped>
.admin-user-manage {
  padding: 20px;
}

.search-bar {
  margin-bottom: 20px;
  max-width: 400px;
}

.pagination {
  margin-top: 20px;
  text-align: right;
}
</style> 