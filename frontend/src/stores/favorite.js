import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { favoriteApi } from '@/services/api';

export const useFavoriteStore = defineStore('favorite', () => {
  // 状态
  const favorites = ref([]);
  const loading = ref(false);
  const error = ref(null);

  // 获取用户的收藏列表
  async function loadFavorites() {
    if (loading.value) return;
    
    loading.value = true;
    error.value = null;

    try {
      const response = await favoriteApi.getFavorites();
      favorites.value = response.favorites || [];
      return favorites.value;
    } catch (err) {
      console.error('Error loading favorites:', err);
      error.value = err.response?.data?.msg || '获取收藏列表失败';
      return [];
    } finally {
      loading.value = false;
    }
  }

  // 添加收藏
  async function addFavorite(itemId) {
    if (loading.value) return;
    
    loading.value = true;
    error.value = null;

    try {
      const response = await favoriteApi.addFavorite(itemId);
      
      // 更新本地收藏列表
      if (response.success) {
        const newFavorite = response.favorite;
        if (!favorites.value.find(fav => fav.item_id === itemId)) {
          favorites.value.push(newFavorite);
        }
      }
      
      return response;
    } catch (err) {
      console.error('Error adding favorite:', err);
      error.value = err.response?.data?.msg || '添加收藏失败';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  // 删除收藏
  async function removeFavorite(itemId) {
    if (loading.value) return;
    
    loading.value = true;
    error.value = null;

    try {
      const response = await favoriteApi.removeFavorite(itemId);
      
      // 更新本地收藏列表
      if (response.success) {
        favorites.value = favorites.value.filter(fav => fav.item_id !== itemId);
      }
      
      return response;
    } catch (err) {
      console.error('Error removing favorite:', err);
      error.value = err.response?.data?.msg || '删除收藏失败';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  // 检查商品是否已收藏
  function isFavorited(itemId) {
    return favorites.value.some(fav => fav.item_id === itemId);
  }

  // 返回所有收藏的商品ID
  const favoriteItemIds = computed(() => {
    return favorites.value.map(fav => fav.item_id);
  });

  return {
    favorites,
    loading,
    error,
    favoriteItemIds,
    loadFavorites,
    addFavorite,
    removeFavorite,
    isFavorited
  };
}); 