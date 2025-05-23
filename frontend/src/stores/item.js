import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { itemApi } from '@/services/api';

export const useItemStore = defineStore('item', () => {
  // 状态
  const items = ref([]);
  const currentItem = ref(null);
  const loading = ref(false);
  const error = ref(null);
  const totalItems = ref(0);
  const currentPage = ref(1);
  const perPage = ref(10);

  // 过滤和搜索条件
  const searchQuery = ref('');
  const categoryFilter = ref('');
  const sortBy = ref('created_at');
  const sortOrder = ref('desc');

  // Getters
  const paginatedItems = computed(() => {
    return items.value;
  });

  const totalPages = computed(() => {
    return Math.ceil(totalItems.value / perPage.value);
  });

  // Actions
  // 获取商品列表
  async function fetchItems(page = 1, resetFilters = false) {
    if (resetFilters) {
      searchQuery.value = '';
      categoryFilter.value = '';
      sortBy.value = 'created_at';
      sortOrder.value = 'desc';
    }

    loading.value = true;
    error.value = null;
    currentPage.value = page;

    try {
      const params = {
        page: page,
        per_page: perPage.value,
        sort_by: sortBy.value,
        sort_order: sortOrder.value
      };

      if (searchQuery.value) {
        params.query = searchQuery.value;
      }

      if (categoryFilter.value) {
        params.category = categoryFilter.value;
      }

      const response = await itemApi.getItems(params);
      console.log('商品列表API响应:', response);
      
      // 适应不同的响应格式
      if (response.data && (response.data.items || response.data.total)) {
        // 如果响应包含data.items和data.total
        items.value = response.data.items || [];
        totalItems.value = response.data.total || 0;
      } else if (response.items || response.total) {
        // 如果响应直接包含items和total
        items.value = response.items || [];
        totalItems.value = response.total || 0;
      } else if (Array.isArray(response)) {
        // 如果响应是一个数组
        items.value = response;
        totalItems.value = response.length;
      } else {
        // 未知响应格式，尝试合理处理
        items.value = [];
        totalItems.value = 0;
        console.error('未知的商品列表响应格式:', response);
      }
      
      return response;
    } catch (err) {
      console.error('Error fetching items:', err);
      error.value = err.response?.data?.msg || '获取商品列表失败';
      items.value = [];
      totalItems.value = 0;
      return null;
    } finally {
      loading.value = false;
    }
  }

  // 获取单个商品详情
  async function fetchItemById(id) {
    loading.value = true;
    error.value = null;

    try {
      const response = await itemApi.getItem(id);
      currentItem.value = response.data;
      return response.data;
    } catch (err) {
      console.error('Error fetching item details:', err);
      error.value = err.response?.data?.msg || '获取商品详情失败';
      return null;
    } finally {
      loading.value = false;
    }
  }

  // 创建新商品
  async function createItem(itemData) {
    loading.value = true;
    error.value = null;

    try {
      const response = await itemApi.createItem(itemData);
      return response.data;
    } catch (err) {
      console.error('Error creating item:', err);
      error.value = err.response?.data?.msg || '创建商品失败';
      return null;
    } finally {
      loading.value = false;
    }
  }

  // 更新商品
  async function updateItem(id, itemData) {
    loading.value = true;
    error.value = null;

    try {
      const response = await itemApi.updateItem(id, itemData);
      
      // 如果当前加载的是这个商品，则更新currentItem
      if (currentItem.value && currentItem.value.id === id) {
        currentItem.value = { ...currentItem.value, ...itemData };
      }
      
      // 更新items列表中的商品
      const index = items.value.findIndex(item => item.id === id);
      if (index !== -1) {
        items.value[index] = { ...items.value[index], ...itemData };
      }
      
      return response.data;
    } catch (err) {
      console.error('Error updating item:', err);
      error.value = err.response?.data?.msg || '更新商品失败';
      return null;
    } finally {
      loading.value = false;
    }
  }

  // 删除商品
  async function deleteItem(id) {
    loading.value = true;
    error.value = null;

    try {
      const response = await itemApi.deleteItem(id);
      
      // 从列表中移除商品
      items.value = items.value.filter(item => item.id !== id);
      
      // 如果当前加载的是这个商品，则清空currentItem
      if (currentItem.value && currentItem.value.id === id) {
        currentItem.value = null;
      }
      
      return response.data;
    } catch (err) {
      console.error('Error deleting item:', err);
      error.value = err.response?.data?.msg || '删除商品失败';
      return null;
    } finally {
      loading.value = false;
    }
  }

  // 设置搜索和过滤条件
  function setSearchQuery(query) {
    searchQuery.value = query;
  }

  function setCategoryFilter(category) {
    categoryFilter.value = category;
  }

  function setSortOptions(sortOption, order) {
    sortBy.value = sortOption;
    sortOrder.value = order;
  }

  return {
    // 状态
    items,
    currentItem,
    loading,
    error,
    totalItems,
    currentPage,
    perPage,
    searchQuery,
    categoryFilter,
    sortBy,
    sortOrder,

    // Getters
    paginatedItems,
    totalPages,

    // Actions
    fetchItems,
    fetchItemById,
    createItem,
    updateItem,
    deleteItem,
    setSearchQuery,
    setCategoryFilter,
    setSortOptions
  };
}); 