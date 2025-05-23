<template>
  <div class="settings-container">
    <el-card class="settings-card">
      <template #header>
        <div class="card-header">
          <h2>个人设置</h2>
        </div>
      </template>
      
      <el-tabs v-model="activeTab">
        <el-tab-pane label="个人资料" name="profile">
          <div class="profile-settings">
            <div class="avatar-section">
              <div class="avatar-container">
                <el-avatar :size="100" :src="avatarUrl" @error="handleAvatarError">
                  <el-icon><User /></el-icon>
                </el-avatar>
                <div class="avatar-overlay" @click="triggerFileInput">
                  <el-icon><Camera /></el-icon>
                  <span>更换头像</span>
                </div>
              </div>
              <input
                type="file"
                ref="avatarInput"
                accept="image/*"
                style="display: none"
                @change="handleAvatarChange"
              />
            </div>
            
            <el-form :model="profileForm" label-width="100px" :rules="profileRules" ref="profileFormRef">
              <el-form-item label="用户名" prop="username">
                <el-input v-model="profileForm.username" placeholder="请输入用户名" />
              </el-form-item>
              
              <el-form-item label="邮箱">
                <el-input v-model="profileForm.email" disabled />
                <div class="form-tip">邮箱不可修改</div>
              </el-form-item>
              
              <el-form-item label="个人简介" prop="bio">
                <el-input
                  v-model="profileForm.bio"
                  type="textarea"
                  :rows="4"
                  placeholder="介绍一下自己吧"
                />
              </el-form-item>
              
              <el-form-item>
                <el-button type="primary" @click="saveProfile" :loading="loading.profile">
                  保存修改
                </el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="修改密码" name="password">
          <div class="password-settings">
            <el-form :model="passwordForm" label-width="120px" :rules="passwordRules" ref="passwordFormRef">
              <el-form-item label="当前密码" prop="currentPassword">
                <el-input
                  v-model="passwordForm.currentPassword"
                  type="password"
                  placeholder="请输入当前密码"
                  show-password
                />
              </el-form-item>
              
              <el-form-item label="新密码" prop="newPassword">
                <el-input
                  v-model="passwordForm.newPassword"
                  type="password"
                  placeholder="请输入新密码"
                  show-password
                />
                <div class="form-tip">密码长度至少为6位</div>
              </el-form-item>
              
              <el-form-item label="确认新密码" prop="confirmPassword">
                <el-input
                  v-model="passwordForm.confirmPassword"
                  type="password"
                  placeholder="请再次输入新密码"
                  show-password
                />
              </el-form-item>
              
              <el-form-item>
                <el-button type="primary" @click="changePassword" :loading="loading.password">
                  修改密码
                </el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { userApi } from '@/services/api';
import { ElMessage } from 'element-plus';
import { User, Camera } from '@element-plus/icons-vue';

const router = useRouter();
const authStore = useAuthStore();

// 状态
const activeTab = ref('profile');
const avatarInput = ref(null);
const profileFormRef = ref(null);
const passwordFormRef = ref(null);
const loading = reactive({
  profile: false,
  password: false
});

// 表单数据
const profileForm = reactive({
  username: '',
  email: '',
  bio: ''
});

const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
});

// 验证规则
const profileRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' }
  ],
  bio: [
    { max: 500, message: '个人简介不能超过500个字符', trigger: 'blur' }
  ]
};

const passwordRules = {
  currentPassword: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少为6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== passwordForm.newPassword) {
          callback(new Error('两次输入的密码不一致'));
        } else {
          callback();
        }
      },
      trigger: 'blur'
    }
  ]
};

// 计算属性
const avatarUrl = computed(() => {
  const baseUrl = import.meta.env.VITE_API_BASE_URL || '';
  if (authStore.user?.avatar) {
    return authStore.user.avatar.startsWith('/static') 
      ? `${baseUrl}${authStore.user.avatar}` 
      : authStore.user.avatar;
  }
  return `${baseUrl}/static/avatars/default_avatar.jpg`;
});

// 初始化
onMounted(async () => {
  if (!authStore.isAuthenticated) {
    ElMessage.warning('请先登录');
    router.push('/login');
    return;
  }
  
  // 刷新用户信息
  await authStore.refreshUserInfo();
  
  // 填充表单
  profileForm.username = authStore.user?.username || '';
  profileForm.email = authStore.user?.email || '';
  profileForm.bio = authStore.user?.bio || '';
});

// 触发文件选择
const triggerFileInput = () => {
  avatarInput.value.click();
};

// 处理头像更改
const handleAvatarChange = async (event) => {
  const file = event.target.files[0];
  if (!file) return;
  
  // 检查文件类型
  if (!file.type.startsWith('image/')) {
    ElMessage.error('请选择图片文件');
    return;
  }
  
  // 检查文件大小（限制为2MB）
  if (file.size > 2 * 1024 * 1024) {
    ElMessage.error('图片大小不能超过2MB');
    return;
  }
  
  try {
    loading.profile = true;
    
    // 上传头像
    const response = await userApi.updateAvatar(file);
    
    // 更新本地用户信息
    await authStore.refreshUserInfo();
    
    ElMessage.success('头像更新成功');
  } catch (error) {
    console.error('头像上传失败:', error);
    ElMessage.error('头像上传失败，请重试');
  } finally {
    loading.profile = false;
    // 清空文件输入，允许重复选择相同文件
    event.target.value = '';
  }
};

// 处理头像加载错误
const handleAvatarError = () => {
  const baseUrl = import.meta.env.VITE_API_BASE_URL || '';
  // 设置为默认头像
  const target = event.target;
  if (target) {
    target.src = `${baseUrl}/static/avatars/default_avatar.jpg`;
  }
};

// 保存个人资料
const saveProfile = async () => {
  if (!profileFormRef.value) return;
  
  await profileFormRef.value.validate(async (valid) => {
    if (!valid) return;
    
    try {
      loading.profile = true;
      
      // 更新用户信息
      await userApi.updateUserInfo({
        username: profileForm.username,
        bio: profileForm.bio
      });
      
      // 刷新用户信息
      await authStore.refreshUserInfo();
      
      ElMessage.success('个人资料更新成功');
    } catch (error) {
      console.error('更新个人资料失败:', error);
      const errorMsg = error.response?.data?.msg || '更新个人资料失败，请重试';
      ElMessage.error(errorMsg);
    } finally {
      loading.profile = false;
    }
  });
};

// 修改密码
const changePassword = async () => {
  if (!passwordFormRef.value) return;
  
  await passwordFormRef.value.validate(async (valid) => {
    if (!valid) return;
    
    try {
      loading.password = true;
      
      // 修改密码
      await userApi.changePassword(
        passwordForm.currentPassword,
        passwordForm.newPassword
      );
      
      // 清空表单
      passwordForm.currentPassword = '';
      passwordForm.newPassword = '';
      passwordForm.confirmPassword = '';
      
      ElMessage.success('密码修改成功');
    } catch (error) {
      console.error('修改密码失败:', error);
      const errorMsg = error.response?.data?.msg || '修改密码失败，请重试';
      ElMessage.error(errorMsg);
    } finally {
      loading.password = false;
    }
  });
};
</script>

<style scoped>
.settings-container {
  max-width: 800px;
  margin: 20px auto;
  padding: 0 20px;
}

.settings-card {
  border-radius: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  font-size: 20px;
}

.avatar-section {
  display: flex;
  justify-content: center;
  margin-bottom: 30px;
}

.avatar-container {
  position: relative;
  width: 100px;
  height: 100px;
  border-radius: 50%;
  overflow: hidden;
}

.avatar-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  color: white;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  opacity: 0;
  transition: opacity 0.3s;
  cursor: pointer;
}

.avatar-overlay:hover {
  opacity: 1;
}

.avatar-overlay .el-icon {
  font-size: 24px;
  margin-bottom: 5px;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .settings-card {
    margin: 0 -10px;
  }
  
  .el-form-item {
    margin-bottom: 18px;
  }
}
</style> 