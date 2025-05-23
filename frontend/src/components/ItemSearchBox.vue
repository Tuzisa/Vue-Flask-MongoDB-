<template>
  <div class="search-box">
    <el-form :model="searchForm" :inline="true" class="search-form" @submit.prevent="handleSearch">
      <!-- 关键词搜索 -->
      <el-form-item>
        <el-input
          v-model="searchForm.keyword"
          placeholder="搜索商品名称"
          clearable
          @clear="handleSearch"
          class="keyword-input"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </el-form-item>

      <!-- 分类筛选 -->
      <el-form-item>
        <el-select
          v-model="searchForm.category"
          placeholder="选择分类"
          clearable
          @change="handleSearch"
          class="category-select"
        >
          <el-option
            v-for="item in categoryOptions"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
      </el-form-item>

      <!-- 价格范围 -->
      <el-form-item>
        <el-popover
          placement="bottom"
          :width="300"
          trigger="click"
          v-model:visible="pricePopoverVisible"
        >
          <template #reference>
            <el-button class="price-range-button">
              价格范围
              <template v-if="hasPriceFilter">
                <el-tag size="small" class="price-tag">
                  {{ searchForm.minPrice || '0' }} - {{ searchForm.maxPrice || '不限' }}
                </el-tag>
              </template>
              <el-icon><ArrowDown /></el-icon>
            </el-button>
          </template>

          <div class="price-range-popover">
            <div class="price-inputs">
              <el-input
                v-model="searchForm.minPrice"
                placeholder="最低价"
                type="number"
                min="0"
              >
                <template #prefix>¥</template>
              </el-input>
              <span class="price-divider">-</span>
              <el-input
                v-model="searchForm.maxPrice"
                placeholder="最高价"
                type="number"
                min="0"
              >
                <template #prefix>¥</template>
              </el-input>
            </div>
            <div class="price-quick-select">
              <el-radio-group v-model="priceRange" @change="handlePriceRangeChange">
                <el-radio label="all">不限</el-radio>
                <el-radio label="0-100">100以下</el-radio>
                <el-radio label="100-500">100-500</el-radio>
                <el-radio label="500-1000">500-1000</el-radio>
                <el-radio label="1000+">1000以上</el-radio>
              </el-radio-group>
            </div>
            <div class="price-actions">
              <el-button @click="resetPriceRange">重置</el-button>
              <el-button type="primary" @click="applyPriceRange">确定</el-button>
            </div>
          </div>
        </el-popover>
      </el-form-item>

      <!-- 排序方式 -->
      <el-form-item>
        <el-select
          v-model="searchForm.sort"
          placeholder="排序方式"
          @change="handleSearch"
          class="sort-select"
        >
          <el-option label="最新发布" value="newest" />
          <el-option label="价格从低到高" value="price_asc" />
          <el-option label="价格从高到低" value="price_desc" />
          <el-option label="最多浏览" value="views" />
        </el-select>
      </el-form-item>

      <!-- 搜索按钮 -->
      <el-form-item>
        <el-button type="primary" @click="handleSearch" class="search-button">
          搜索
        </el-button>
        <el-button @click="resetSearch" plain>重置</el-button>
      </el-form-item>
    </el-form>

    <!-- 已选筛选条件 -->
    <div v-if="hasFilters" class="selected-filters">
      <span class="filters-title">已选条件：</span>
      <div class="filters-tags">
        <el-tag
          v-if="searchForm.keyword"
          closable
          @close="clearFilter('keyword')"
          class="filter-tag"
        >
          关键词: {{ searchForm.keyword }}
        </el-tag>

        <el-tag
          v-if="searchForm.category"
          closable
          @close="clearFilter('category')"
          class="filter-tag"
        >
          分类: {{ getCategoryLabel(searchForm.category) }}
        </el-tag>

        <el-tag
          v-if="hasPriceFilter"
          closable
          @close="clearFilter('price')"
          class="filter-tag"
        >
          价格: {{ searchForm.minPrice || '0' }} - {{ searchForm.maxPrice || '不限' }}
        </el-tag>

        <el-button v-if="hasFilters" link type="danger" @click="resetSearch">
          清除全部
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue';
import { Search, ArrowDown } from '@element-plus/icons-vue';

const props = defineProps({
  initialFilters: {
    type: Object,
    default: () => ({})
  }
});

const emit = defineEmits(['search']);

// 分类选项
const categoryOptions = [
  { value: 'electronics', label: '电子产品' },
  { value: 'clothing', label: '服装' },
  { value: 'books', label: '图书' },
  { value: 'furniture', label: '家具' },
  { value: 'other', label: '其他' }
];

// 搜索表单数据
const searchForm = reactive({
  keyword: props.initialFilters.keyword || '',
  category: props.initialFilters.category || '',
  minPrice: props.initialFilters.minPrice || '',
  maxPrice: props.initialFilters.maxPrice || '',
  sort: props.initialFilters.sort || 'newest'
});

// 价格范围弹窗可见性
const pricePopoverVisible = ref(false);
// 价格范围快速选择
const priceRange = ref('all');

// 计算是否有价格筛选
const hasPriceFilter = computed(() => {
  return searchForm.minPrice || searchForm.maxPrice;
});

// 计算是否有任何筛选条件
const hasFilters = computed(() => {
  return searchForm.keyword || 
         searchForm.category || 
         searchForm.minPrice || 
         searchForm.maxPrice || 
         searchForm.sort !== 'newest';
});

// 处理搜索
const handleSearch = () => {
  // 发出搜索事件，传递搜索参数
  emit('search', { ...searchForm });
};

// 处理价格区间快速选择变化
const handlePriceRangeChange = (value) => {
  switch (value) {
    case 'all':
      searchForm.minPrice = '';
      searchForm.maxPrice = '';
      break;
    case '0-100':
      searchForm.minPrice = 0;
      searchForm.maxPrice = 100;
      break;
    case '100-500':
      searchForm.minPrice = 100;
      searchForm.maxPrice = 500;
      break;
    case '500-1000':
      searchForm.minPrice = 500;
      searchForm.maxPrice = 1000;
      break;
    case '1000+':
      searchForm.minPrice = 1000;
      searchForm.maxPrice = '';
      break;
  }
};

// 应用价格筛选
const applyPriceRange = () => {
  // 验证价格输入
  if (searchForm.minPrice && searchForm.maxPrice) {
    // 转换为数字进行比较
    const minPrice = Number(searchForm.minPrice);
    const maxPrice = Number(searchForm.maxPrice);
    
    if (minPrice > maxPrice) {
      // 如果最低价高于最高价，交换它们
      searchForm.minPrice = maxPrice;
      searchForm.maxPrice = minPrice;
    }
  }
  
  // 确保价格是数字类型
  if (searchForm.minPrice !== '') {
    searchForm.minPrice = Number(searchForm.minPrice);
  }
  if (searchForm.maxPrice !== '') {
    searchForm.maxPrice = Number(searchForm.maxPrice);
  }
  
  pricePopoverVisible.value = false;
  handleSearch();
};

// 重置价格范围
const resetPriceRange = () => {
  searchForm.minPrice = '';
  searchForm.maxPrice = '';
  priceRange.value = 'all';
};

// 重置搜索
const resetSearch = () => {
  searchForm.keyword = '';
  searchForm.category = '';
  searchForm.minPrice = '';
  searchForm.maxPrice = '';
  searchForm.sort = 'newest';
  priceRange.value = 'all';
  handleSearch();
};

// 清除单个筛选条件
const clearFilter = (type) => {
  if (type === 'keyword') {
    searchForm.keyword = '';
  } else if (type === 'category') {
    searchForm.category = '';
  } else if (type === 'price') {
    searchForm.minPrice = '';
    searchForm.maxPrice = '';
    priceRange.value = 'all';
  }
  handleSearch();
};

// 获取分类的显示标签
const getCategoryLabel = (value) => {
  const category = categoryOptions.find(item => item.value === value);
  return category ? category.label : value;
};
</script>

<style scoped>
.search-box {
  margin-bottom: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  padding: 16px;
}

.search-form {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.keyword-input {
  width: 200px;
}

.category-select,
.sort-select {
  width: 150px;
}

.price-range-button {
  display: flex;
  align-items: center;
  gap: 5px;
}

.price-tag {
  margin-left: 5px;
  margin-right: 5px;
}

.price-range-popover {
  padding: 10px;
}

.price-inputs {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.price-divider {
  margin: 0 10px;
  color: #909399;
}

.price-quick-select {
  margin-bottom: 15px;
}

.price-quick-select :deep(.el-radio-group) {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.price-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.selected-filters {
  margin-top: 15px;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
}

.filters-title {
  font-size: 14px;
  color: #606266;
  margin-right: 10px;
}

.filters-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}

.filter-tag {
  background-color: #f0f9eb;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .search-form {
    flex-direction: column;
  }
  
  .keyword-input,
  .category-select,
  .sort-select {
    width: 100%;
  }
  
  .price-range-button {
    width: 100%;
    justify-content: space-between;
  }
  
  .price-inputs {
    flex-direction: column;
    gap: 10px;
  }
  
  .price-divider {
    display: none;
  }
}
</style> 