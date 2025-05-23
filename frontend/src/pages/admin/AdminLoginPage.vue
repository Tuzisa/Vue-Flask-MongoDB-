<template>
  <div class="admin-login-container">
    <div class="admin-login-box">
      <div class="admin-login-header">
        <h2>管理员登录</h2>
      </div>
      
      <el-form 
        ref="formRef"
        :model="loginForm"
        :rules="loginRules"
        label-position="top"
        @submit.prevent="handleLogin"
      >
        <el-form-item label="管理员账号" prop="email">
          <el-input 
            v-model="loginForm.email"
            placeholder="请输入管理员邮箱"
          >
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input 
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            show-password
          >
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <div class="error-message" v-if="errorMessage">{{ errorMessage }}</div>
        
        <el-form-item>
          <el-button 
            type="primary" 
            native-type="submit" 
            :loading="loading"
            class="login-button"
          >登录</el-button>
          <el-button @click="$router.push('/')" plain>返回首页</el-button>
        </el-form-item>
      </el-form>
      
      <div class="debug-info">
        <p>默认管理员账号: admin@example.com</p>
        <p>默认密码: admin123</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { ElMessage } from 'element-plus';
import { User, Lock } from '@element-plus/icons-vue';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const formRef = ref(null);
const loading = ref(false);
const errorMessage = ref('');

// 表单数据
const loginForm = reactive({
  email: 'admin@example.com',  // 预填默认管理员邮箱
  password: 'admin123'         // 预填默认密码
});

// 表单验证规则
const loginRules = {
  email: [
    { required: true, message: '请输入管理员邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少为6个字符', trigger: 'blur' }
  ]
};

// 处理登录
const handleLogin = async () => {
  if (!formRef.value) return;
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return;
    
    loading.value = true;
    errorMessage.value = '';
    
    try {
      console.log('尝试简化管理员登录:', loginForm);
      
      // 使用简化的管理员登录方法
      const success = await authStore.adminSimpleLogin({
        email: loginForm.email,
        password: loginForm.password
      });
      
      console.log('登录结果:', success, '错误信息:', authStore.error);
      
      if (success) {
        ElMessage.success('管理员登录成功');
        router.push('/admin/dashboard');
      } else {
        errorMessage.value = authStore.error || '登录失败，请检查账号和密码';
        console.error('管理员登录失败:', authStore.error);
      }
    } catch (error) {
      console.error('登录出错:', error);
      errorMessage.value = '登录过程中出现错误: ' + (error.message || '未知错误');
    } finally {
      loading.value = false;
    }
  });
};

// 监听authStore中的错误信息变化
watch(() => authStore.error, (newError) => {
  if (newError) {
    errorMessage.value = newError;
  }
});

// 在组件挂载时检查是否已经登录
onMounted(() => {
  // 如果已经是管理员登录状态，直接跳转到仪表盘
  if (authStore.isAuthenticated && authStore.isAdmin) {
    router.push('/admin/dashboard');
  }
  
  // 如果是从其他需要管理员权限的页面重定向过来的，显示错误信息
  if (route.query.unauthorized) {
    errorMessage.value = '您需要管理员权限才能访问该页面';
  }
});
</script>

<style scoped>
.admin-login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 200px);
  padding: 20px;
}

.admin-login-box {
  width: 100%;
  max-width: 400px;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  background-color: #fff;
}

.admin-login-header {
  text-align: center;
  margin-bottom: 30px;
}

.admin-login-header h2 {
  font-size: 24px;
  color: #409EFF;
  margin: 0;
}

.login-button {
  width: 100%;
  margin-bottom: 15px;
}

.error-message {
  color: #F56C6C;
  font-size: 14px;
  margin-bottom: 15px;
}

.debug-info {
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px dashed #dcdfe6;
  font-size: 12px;
  color: #909399;
  text-align: center;
}
</style> 