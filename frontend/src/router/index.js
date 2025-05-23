import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import adminRoutes from './admin'
// 懒加载组件，提高初始加载速度
const ItemListView = () => import('@/pages/ItemListPage.vue')
const PublishItemView = () => import('@/pages/PublishItemPage.vue')
const LoginRegisterView = () => import('@/pages/LoginRegisterPage.vue')
const ItemDetailView = () => import('@/pages/ItemDetailPage.vue')
const UserProfileView = () => import('@/pages/UserProfilePage.vue')
const UserSettingsView = () => import('@/pages/UserSettingsPage.vue')
// 首页使用专门的首页组件
const HomeView = () => import('@/pages/HomePage.vue')
const PurchasePageView = () => import('@/pages/PurchasePage.vue')

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomeView
  },
  {
    path: '/items',
    name: 'ItemList',
    component: ItemListView
  },
  {
    path: '/publish',
    name: 'PublishItem',
    component: PublishItemView,
    meta: { requiresAuth: true } // 需要登录才能访问的路由
  },
  {
    path: '/edit/:id',
    name: 'EditItem',
    component: PublishItemView, // 复用发布商品的组件
    meta: { requiresAuth: true, isEdit: true } // 标记为编辑模式
  },
  {
    path: '/login',
    name: 'LoginRegister',
    component: LoginRegisterView
  },
  {
    path: '/item/:id',
    name: 'ItemDetail',
    component: ItemDetailView
  },
  {
    path: '/profile',
    name: 'UserProfile',
    component: UserProfileView,
    meta: { requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'UserSettings',
    component: UserSettingsView,
    meta: { requiresAuth: true }
  },
  {
    path: '/purchase/:itemId',
    name: 'PurchasePage',
    component: PurchasePageView,
    meta: { requiresAuth: true }
  },
  // 添加管理路由
  ...adminRoutes
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL), // 使用 HTML5 History 模式
  routes
})

// 路由守卫，用于登录验证
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();
  
  // 检查是否需要管理员权限
  if (to.meta.requiresAdmin) {
    if (!authStore.isAuthenticated) {
      // 如果未登录，跳转到管理员登录页
      next({ 
        name: 'AdminLogin',
        query: { unauthorized: true }
      });
    } else if (!authStore.isAdmin) {
      // 如果已登录但不是管理员，跳转到管理员登录页并提示权限不足
      next({ 
        name: 'AdminLogin',
        query: { unauthorized: true }
      });
    } else {
      // 是管理员，允许访问
      next();
    }
  } 
  // 检查路由是否需要普通用户认证
  else if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    // 如果需要认证但用户未登录，则跳转到登录页
    next({ 
      name: 'LoginRegister', 
      query: { redirect: to.fullPath } // 保存原来要去的路径，便于登录后重定向
    });
  } else {
    // 正常导航
    next();
  }
});

export default router 