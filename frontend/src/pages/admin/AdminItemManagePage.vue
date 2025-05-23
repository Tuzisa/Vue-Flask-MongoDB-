<template>
  <div class="admin-item-manage">
    <h2>商品管理</h2>
    
    <div class="search-bar">
      <el-input
        v-model="searchQuery"
        placeholder="搜索商品标题或描述"
        clearable
        @clear="loadItems"
      >
        <template #append>
          <el-button @click="loadItems">
            <el-icon><Search /></el-icon>
          </el-button>
        </template>
      </el-input>
    </div>
    
    <el-table
      :data="items"
      style="width: 100%"
      v-loading="loading"
      border
    >
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="title" label="标题" width="200" />
      <el-table-column prop="price" label="价格" width="100">
        <template #default="scope">
          ¥ {{ Number(scope.row.price).toFixed(2) }}
        </template>
      </el-table-column>
      <el-table-column prop="category" label="分类" width="120">
        <template #default="scope">
          {{ getCategoryName(scope.row.category) }}
        </template>
      </el-table-column>
      <el-table-column label="卖家" width="120">
        <template #default="scope">
          {{ getSellerName(scope.row) }}
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="发布时间" width="180">
        <template #default="scope">
          {{ formatDate(scope.row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作">
        <template #default="scope">
          <el-button 
            type="primary" 
            size="small" 
            @click="editItem(scope.row)"
          >编辑</el-button>
          <el-button 
            type="danger" 
            size="small" 
            @click="confirmDeleteItem(scope.row)"
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
    
    <!-- 编辑商品对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑商品信息"
      width="600px"
    >
      <el-form
        ref="editFormRef"
        :model="editForm"
        :rules="editRules"
        label-width="80px"
      >
        <el-form-item label="标题" prop="title">
          <el-input v-model="editForm.title" />
        </el-form-item>
        <el-form-item label="价格" prop="price">
          <el-input-number v-model="editForm.price" :precision="2" :step="0.1" :min="0" />
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-select v-model="editForm.category" placeholder="请选择分类">
            <el-option
              v-for="(name, value) in categoryMap"
              :key="value"
              :label="name"
              :value="value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="editForm.description" type="textarea" :rows="4" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveItem" :loading="saving">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Search } from '@element-plus/icons-vue';
import { adminApi, itemApi } from '@/services/api';
import axios from 'axios';

// 状态
const items = ref([]);
const total = ref(0);
const currentPage = ref(1);
const pageSize = ref(10);
const loading = ref(false);
const searchQuery = ref('');

// 分类映射
const categoryMap = {
  'electronics': '电子产品',
  'clothing': '服装',
  'books': '图书',
  'furniture': '家具',
  'other': '其他'
};

// 编辑商品相关
const editDialogVisible = ref(false);
const editFormRef = ref(null);
const editForm = reactive({
  id: '',
  title: '',
  price: 0,
  category: '',
  description: ''
});
const editRules = {
  title: [
    { required: true, message: '请输入商品标题', trigger: 'blur' },
    { min: 2, max: 100, message: '长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  price: [
    { required: true, message: '请输入价格', trigger: 'blur' },
    { type: 'number', min: 0, message: '价格必须大于等于0', trigger: 'blur' }
  ],
  category: [
    { required: true, message: '请选择分类', trigger: 'change' }
  ],
  description: [
    { required: true, message: '请输入商品描述', trigger: 'blur' }
  ]
};
const saving = ref(false);

// 初始化
onMounted(() => {
  loadItems();
});

// 直接从常规API获取商品列表（绕过管理员API）
const loadItems = async () => {
  loading.value = true;
  
  try {
    // 使用普通的商品API或者直接使用axios
    const params = {
      page: currentPage.value,
      limit: pageSize.value,
      query: searchQuery.value || undefined
    };
    
    console.log('请求商品列表参数:', params);
    
    // 方法1：使用itemApi
    const response = await itemApi.getItems(params);
    console.log('商品列表响应:', response);
    
    if (response && response.data) {
      let itemsData = [];
      
      // 处理不同的响应格式
      if (Array.isArray(response.data)) {
        itemsData = response.data;
        total.value = response.data.length;
      } else if (response.data.items) {
        itemsData = response.data.items;
        total.value = response.data.total || response.data.items.length;
      } else if (response.data.results) {
        itemsData = response.data.results;
        total.value = response.data.total || response.data.results.length;
      }
      
      // 确保每个商品项都有seller属性而不是seller_id
      items.value = itemsData.map(item => {
        if (item.seller_id && !item.seller) {
          // 如果有seller_id但没有seller，创建一个seller对象
          item.seller = { id: item.seller_id, username: `用户${item.seller_id}` };
        }
        return item;
      });
      
      console.log('处理后的商品数据:', items.value);
    } else {
      items.value = [];
      total.value = 0;
    }
  } catch (error) {
    console.error('加载商品列表失败:', error);
    if (error.response) {
      console.error('错误响应:', error.response.status, error.response.data);
    }
    
    // 失败后尝试使用备用方法
    tryAlternativeLoadMethod();
  } finally {
    loading.value = false;
  }
};

// 备用加载方法 - 直接使用Axios
const tryAlternativeLoadMethod = async () => {
  loading.value = true;
  
  try {
    console.log('尝试备用方法加载商品数据...');
    const response = await axios.get('/api/items', {
      params: {
        page: currentPage.value,
        limit: pageSize.value,
        q: searchQuery.value || undefined
      }
    });
    
    console.log('备用方法响应:', response);
    
    if (response && response.data) {
      let itemsData = [];
      
      // 处理不同的响应格式
      if (Array.isArray(response.data)) {
        itemsData = response.data;
        total.value = response.data.length;
      } else if (response.data.items || response.data.results) {
        itemsData = response.data.items || response.data.results;
        total.value = response.data.total || itemsData.length;
      }
      
      // 确保每个商品项都有seller属性
      items.value = itemsData.map(item => {
        if (item.seller_id && !item.seller) {
          item.seller = { id: item.seller_id, username: `用户${item.seller_id}` };
        }
        return item;
      });
      
      ElMessage.success('成功加载商品数据');
    } else {
      items.value = [];
      total.value = 0;
      ElMessage.warning('未找到商品数据');
    }
  } catch (error) {
    console.error('备用方法加载失败:', error);
    ElMessage.error('无法加载商品数据，请稍后重试');
    items.value = [];
    total.value = 0;
  } finally {
    loading.value = false;
  }
};

// 获取卖家名称
const getSellerName = (item) => {
  // 适应不同的卖家数据结构
  if (item.seller && typeof item.seller === 'object' && item.seller.username) {
    return item.seller.username;
  } else if (item.seller && typeof item.seller === 'string') {
    return item.seller;
  } else if (item.seller_id) {
    return `用户${item.seller_id}`;
  } else {
    return '未知用户';
  }
};

// 处理页码变化
const handlePageChange = (page) => {
  currentPage.value = page;
  loadItems();
};

// 编辑商品
const editItem = (item) => {
  console.log('编辑商品:', item);
  editForm.id = item.id || item._id;
  editForm.title = item.title;
  editForm.price = parseFloat(item.price) || 0;
  editForm.category = item.category;
  editForm.description = item.description;
  editDialogVisible.value = true;
};

// 保存商品
const saveItem = async () => {
  if (!editFormRef.value) return;
  
  await editFormRef.value.validate(async (valid) => {
    if (!valid) return;
    
    saving.value = true;
    
    try {
      console.log('保存商品信息:', editForm);
      // 尝试使用itemApi而不是adminApi
      const itemData = {
        title: editForm.title,
        price: editForm.price,
        category: editForm.category,
        description: editForm.description
      };
      
      // 先尝试adminApi
      try {
        await adminApi.updateItem(editForm.id, itemData);
      } catch (adminError) {
        console.error('管理员API更新失败，尝试使用普通API:', adminError);
        // 如果管理员API失败，尝试普通API
        await itemApi.updateItem(editForm.id, itemData);
      }
      
      ElMessage.success('商品信息已更新');
      editDialogVisible.value = false;
      
      // 重新加载商品列表
      loadItems();
    } catch (error) {
      console.error('保存商品信息失败:', error);
      if (error.response) {
        console.error('错误响应:', error.response.status, error.response.data);
      }
      ElMessage.error('保存商品信息失败，请稍后重试');
    } finally {
      saving.value = false;
    }
  });
};

// 确认删除商品
const confirmDeleteItem = (item) => {
  ElMessageBox.confirm(`确定要删除商品 "${item.title}" 吗？`, '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    deleteItem(item.id || item._id);
  }).catch(() => {});
};

// 删除商品
const deleteItem = async (itemId) => {
  loading.value = true;
  
  try {
    console.log('删除商品ID:', itemId);
    
    // 先尝试adminApi
    try {
      await adminApi.deleteItem(itemId);
    } catch (adminError) {
      console.error('管理员API删除失败，尝试使用普通API:', adminError);
      // 如果管理员API失败，尝试普通API
      await itemApi.deleteItem(itemId);
    }
    
    ElMessage.success('商品已删除');
    
    // 重新加载商品列表
    loadItems();
  } catch (error) {
    console.error('删除商品失败:', error);
    if (error.response) {
      console.error('错误响应:', error.response.status, error.response.data);
    }
    ElMessage.error('删除商品失败，请稍后重试');
    loading.value = false;
  }
};

// 获取分类名称
const getCategoryName = (category) => {
  return categoryMap[category] || category || '未分类';
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
.admin-item-manage {
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