import AdminLoginPage from '../pages/admin/AdminLoginPage.vue'
import AdminDashboardPage from '../pages/admin/AdminDashboardPage.vue'
import AdminUserManagePage from '../pages/admin/AdminUserManagePage.vue'
import AdminItemManagePage from '../pages/admin/AdminItemManagePage.vue'
import AdminCommentManagePage from '../pages/admin/AdminCommentManagePage.vue'

const adminRoutes = [
  {
    path: '/admin/login',
    name: 'AdminLogin',
    component: AdminLoginPage,
    meta: {
      title: '管理员登录',
      requiresAuth: false
    }
  },
  {
    path: '/admin/dashboard',
    name: 'AdminDashboard',
    component: AdminDashboardPage,
    meta: {
      title: '管理后台',
      requiresAuth: true,
      requiresAdmin: true
    }
  },
  {
    path: '/admin/users',
    name: 'AdminUserManage',
    component: AdminUserManagePage,
    meta: {
      title: '用户管理',
      requiresAuth: true,
      requiresAdmin: true
    }
  },
  {
    path: '/admin/items',
    name: 'AdminItemManage',
    component: AdminItemManagePage,
    meta: {
      title: '商品管理',
      requiresAuth: true,
      requiresAdmin: true
    }
  },
  {
    path: '/admin/comments',
    name: 'AdminCommentManage',
    component: AdminCommentManagePage,
    meta: {
      title: '评论管理',
      requiresAuth: true,
      requiresAdmin: true
    }
  }
]

export default adminRoutes 