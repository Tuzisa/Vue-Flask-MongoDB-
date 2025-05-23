<template>
  <div class="image-uploader">
    <input 
      type="file" 
      ref="fileInput"
      @change="handleFileChange" 
      accept="image/*" 
      multiple
      :disabled="isUploading"
      style="display: none"
    />
    
    <div class="upload-area" @click="triggerFileInput" :class="{ 'is-uploading': isUploading }">
      <div v-if="isUploading" class="upload-loading">
        <el-icon class="loading-icon"><Loading /></el-icon>
        <span>上传中...</span>
      </div>
      <div v-else class="upload-placeholder">
        <el-icon><Upload /></el-icon>
        <span>点击上传图片</span>
        <div class="upload-hint">支持 JPG、PNG 格式，最多 5 张</div>
      </div>
    </div>
    
    <div class="preview-list" v-if="previewImages.length > 0">
      <div v-for="(img, index) in previewImages" :key="index" class="preview-item">
        <img :src="img.url" :alt="img.name" class="preview-image" />
        <div class="preview-info">
          <span class="preview-name">{{ img.name }}</span>
          <el-button 
            type="danger" 
            size="small" 
            circle 
            @click="removeImage(index)" 
            class="remove-btn"
            :disabled="isUploading"
          >
            <el-icon><Delete /></el-icon>
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { ElMessage } from 'element-plus';
import { Upload, Delete, Loading } from '@element-plus/icons-vue';

const props = defineProps({
  maxImages: {
    type: Number,
    default: 5
  },
  initialImages: {
    type: Array,
    default: () => []
  }
});

const emit = defineEmits(['update:images']);

const fileInput = ref(null);
const previewImages = ref([...props.initialImages]);
const isUploading = ref(false);

// 触发文件选择
const triggerFileInput = () => {
  if (isUploading.value) return;
  fileInput.value.click();
};

// 处理文件选择
const handleFileChange = async (event) => {
  const files = event.target.files;
  if (!files || files.length === 0) return;
  
  // 检查是否超过最大数量
  if (previewImages.value.length + files.length > props.maxImages) {
    ElMessage.warning(`最多只能上传${props.maxImages}张图片`);
    return;
  }
  
  isUploading.value = true;
  
  try {
    // 模拟上传图片（实际项目中应该调用真实的上传API）
    const uploadedImages = await simulateImageUpload(files);
    
    // 添加到预览图片列表
    previewImages.value = [...previewImages.value, ...uploadedImages];
    
    // 通知父组件
    emitImagesUpdate();
    
    // 清空文件输入，允许重复选择相同文件
    event.target.value = '';
    
    ElMessage.success('图片上传成功');
  } catch (error) {
    console.error('图片上传失败:', error);
    ElMessage.error('图片上传失败，请重试');
  } finally {
    isUploading.value = false;
  }
};

// 模拟图片上传（实际项目中应替换为真实上传API）
const simulateImageUpload = (files) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const images = Array.from(files).map((file, index) => {
        // 创建本地预览URL
        const previewUrl = URL.createObjectURL(file);
        
        // 创建唯一文件名
        const timestamp = Date.now();
        const randomStr = Math.floor(Math.random() * 1000);
        const fileName = `${timestamp}_${randomStr}_${file.name.replace(/[^a-zA-Z0-9.]/g, '_')}`;
        
        // 模拟服务器URL
        const serverPath = `/images/uploads/${fileName}`;
        
        return {
          file,
          name: file.name,
          url: previewUrl,    // 本地预览URL
          path: serverPath,   // 模拟服务器路径（实际项目中应该是从服务器返回的URL）
          size: file.size,
          type: file.type
        };
      });
      
      resolve(images);
    }, 1000); // 模拟1秒的上传时间
  });
};

// 移除图片
const removeImage = (index) => {
  // 释放URL对象避免内存泄漏
  if (previewImages.value[index].url && previewImages.value[index].url.startsWith('blob:')) {
    URL.revokeObjectURL(previewImages.value[index].url);
  }
  
  // 从数组中移除
  previewImages.value.splice(index, 1);
  
  // 通知父组件
  emitImagesUpdate();
};

// 向父组件发送更新后的图片列表
const emitImagesUpdate = () => {
  // 提取我们需要的图片信息
  const images = previewImages.value.map(img => ({
    url: img.path || img.url, // 优先使用服务器路径
    name: img.name,
    type: img.type || 'image/jpeg'
  }));
  
  emit('update:images', images);
};
</script>

<style scoped>
.image-uploader {
  margin-bottom: 20px;
}

.upload-area {
  border: 2px dashed #dcdfe6;
  border-radius: 6px;
  padding: 30px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
}

.upload-area:hover {
  border-color: #409eff;
}

.upload-area.is-uploading {
  cursor: not-allowed;
  background-color: #f5f7fa;
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: #606266;
}

.upload-placeholder .el-icon {
  font-size: 28px;
  margin-bottom: 8px;
  color: #c0c4cc;
}

.upload-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: #409eff;
}

.loading-icon {
  animation: rotating 2s linear infinite;
  margin-bottom: 8px;
  font-size: 28px;
}

.upload-hint {
  font-size: 12px;
  margin-top: 8px;
  color: #909399;
}

.preview-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 15px;
}

.preview-item {
  width: 150px;
  border-radius: 4px;
  overflow: hidden;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.preview-image {
  width: 100%;
  height: 100px;
  object-fit: cover;
  display: block;
}

.preview-info {
  padding: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #f5f7fa;
}

.preview-name {
  font-size: 12px;
  color: #606266;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100px;
}

.remove-btn {
  flex-shrink: 0;
}

@keyframes rotating {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style> 