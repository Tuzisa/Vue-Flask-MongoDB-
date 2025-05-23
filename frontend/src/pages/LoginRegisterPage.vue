<template>
  <div class="login-register-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>{{ isLoginMode ? '欢迎回来' : '加入我们' }}</span>
          <el-button type="primary" link @click="toggleMode">
            {{ isLoginMode ? '还没有账户？去注册' : '已有账户？去登录' }}
          </el-button>
        </div>
      </template>
      <el-form ref="formRef" :model="formData" :rules="formRules" label-position="top" @submit.prevent="handleSubmit">
        <el-form-item v-if="!isLoginMode" label="用户名" prop="username">
          <el-input v-model="formData.username" placeholder="请输入用户名" clearable />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="formData.email" placeholder="请输入邮箱" type="email" clearable />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="formData.password" placeholder="请输入密码" type="password" show-password clearable />
        </el-form-item>
        <el-form-item v-if="!isLoginMode" label="确认密码" prop="confirmPassword">
          <el-input v-model="formData.confirmPassword" placeholder="请再次输入密码" type="password" show-password clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" native-type="submit" class="submit-button" :loading="loading">
            {{ isLoginMode ? '登录' : '注册' }}
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue';
import { ElMessage, ElCard, ElForm, ElFormItem, ElInput, ElButton } from 'element-plus';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/auth'; // 引入 Pinia Store

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

const isLoginMode = ref(true); // true 为登录模式，false 为注册模式
const loading = ref(false);
const formRef = ref(null); // 表单引用

const formData = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
});

// 表单校验规则
const validatePass = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请输入密码'));
  } else {
    if (!isLoginMode.value && formData.confirmPassword !== '') {
      if (!formRef.value) return;
      formRef.value.validateField('confirmPassword', () => null);
    }
    callback();
  }
};
const validateConfirmPass = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入密码'));
  } else if (value !== formData.password) {
    callback(new Error("两次输入的密码不一致!"));
  } else {
    callback();
  }
};

const formRules = computed(() => ({
  username: [
    { required: !isLoginMode.value, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: ['blur', 'change'] }
  ],
  password: [
    { required: true, validator: validatePass, trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: !isLoginMode.value, validator: validateConfirmPass, trigger: 'blur' }
  ]
}));

const toggleMode = () => {
  isLoginMode.value = !isLoginMode.value;
  formRef.value?.resetFields(); // 切换模式时重置表单
};

const handleSubmit = async () => {
  if (!formRef.value) return;
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true;
      try {
        if (isLoginMode.value) {
          // 登录逻辑
          const success = await authStore.login({
            email: formData.email,
            password: formData.password
          });
          if (success) {
            ElMessage.success('登录成功！正在跳转...');
            
            // 获取重定向URL（如果存在）
            const redirectUrl = route.query.redirect || '/';
            router.push(redirectUrl);
          } else {
            // authStore.login 内部已处理错误提示，这里可以不再重复提示，或根据返回的特定错误码处理
            // ElMessage.error(authStore.error || '邮箱或密码错误');
          }
        } else {
          // 注册逻辑
          const success = await authStore.register({
            username: formData.username,
            email: formData.email,
            password: formData.password
          });
          if (success) {
            ElMessage.success('注册成功！请登录。');
            isLoginMode.value = true; // 注册成功后切换到登录模式
            formRef.value?.resetFields();
          } else {
            // ElMessage.error(authStore.error || '注册失败，请稍后再试');
          }
        }
      } catch (error) {
        // Pinia store 中的 action 应该处理自己的错误并通过 ElMessage 显示
        // 如果 store action 抛出错误，这里可以捕获并显示通用错误信息
        ElMessage.error(error.response?.data?.msg || error.message || (isLoginMode.value ? '登录失败' : '注册失败'));
      } finally {
        loading.value = false;
      }
    } else {
      ElMessage.error('请检查表单输入项');
      return false;
    }
  });
};

</script>

<style scoped>
.login-register-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 100px); /* 减去可能的页头页尾高度 */
  background-color: #fef0f0; /* 淡粉色背景 */
  padding: 20px;
}

.box-card {
  width: 400px;
  border-radius: 12px; /* 圆角 */
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08); /* 更柔和的阴影 */
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 1.2em;
  color: #333;
}

.card-header span {
  font-weight: bold;
}

.submit-button {
  width: 100%;
  background-color: #f77ca2; /* 主题粉色 */
  border-color: #f77ca2;
  border-radius: 8px;
  transition: background-color 0.3s ease, border-color 0.3s ease;
}

.submit-button:hover {
  background-color: #e06295; /* Hover 颜色 */
  border-color: #e06295;
}

/* Element Plus 表单项样式微调 */
:deep(.el-form-item__label) {
  color: #555;
  padding-bottom: 4px; /* 标签和输入框间距 */
}

:deep(.el-input__inner) {
  border-radius: 8px; /* 输入框圆角 */
}

:deep(.el-card__header) {
  background-color: #fff9f9; /* 卡片头部淡一点的粉色 */
  border-bottom: 1px solid #fde2e2;
}
</style> 