<template>
  <div class="simple-image-uploader">
    <div class="upload-container">
      <label for="image-upload" class="upload-label">
        <div class="upload-button">
          <span class="upload-icon">+</span>
          <span>点击上传图片</span>
          <p class="upload-tip">支持jpg、png格式，最多{{ maxImages }}张</p>
        </div>
      </label>
      <input 
        type="file" 
        id="image-upload" 
        accept="image/*" 
        multiple
        @change="handleFileChange"
        style="display: none"
      />
    </div>
    
    <div class="preview-container" v-if="previewUrls.length > 0">
      <div v-for="(url, index) in previewUrls" :key="index" class="preview-item">
        <img :src="url" :alt="'图片 ' + (index + 1)" class="preview-image">
        <button @click="removeImage(index)" class="delete-button">×</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  },
  maxImages: {
    type: Number,
    default: 5
  }
});

const emit = defineEmits(['update:modelValue']);

const imageFiles = ref([]);
const previewUrls = ref([]);

// 处理文件选择
const handleFileChange = (event) => {
  const files = event.target.files;
  if (!files.length) return;
  
  // 检查是否超过最大数量
  if (imageFiles.value.length + files.length > props.maxImages) {
    alert(`最多只能上传${props.maxImages}张图片`);
    return;
  }
  
  // 处理每个文件
  Array.from(files).forEach(file => {
    // 检查文件类型
    if (!file.type.match('image.*')) {
      alert('请只上传图片文件');
      return;
    }
    
    // 保存文件
    imageFiles.value.push(file);
    
    // 创建预览URL
    const reader = new FileReader();
    reader.onload = e => {
      previewUrls.value.push(e.target.result);
      updateModelValue();
    };
    reader.readAsDataURL(file);
  });
  
  // 重置输入框，允许重复选择相同文件
  event.target.value = '';
};

// 移除图片
const removeImage = (index) => {
  imageFiles.value.splice(index, 1);
  previewUrls.value.splice(index, 1);
  updateModelValue();
};

// 更新v-model值
const updateModelValue = () => {
  // 准备图片信息
  const images = imageFiles.value.map((file, index) => {
    return {
      file: file,
      url: previewUrls.value[index],
      name: file.name,
      type: file.type
    };
  });
  
  // 发送到父组件
  emit('update:modelValue', images);
};

// 如果外部传入值变化，也更新本地状态
watch(() => props.modelValue, (newVal) => {
  if (newVal.length === 0 && imageFiles.value.length > 0) {
    // 如果外部值被清空，也清空本地状态
    imageFiles.value = [];
    previewUrls.value = [];
  }
}, { deep: true });
</script>

<style scoped>
.simple-image-uploader {
  margin-bottom: 20px;
}

.upload-container {
  margin-bottom: 15px;
}

.upload-label {
  display: block;
  cursor: pointer;
}

.upload-button {
  border: 2px dashed #ddd;
  border-radius: 6px;
  padding: 25px 15px;
  text-align: center;
  color: #666;
  transition: all 0.3s;
}

.upload-button:hover {
  border-color: #409EFF;
  color: #409EFF;
}

.upload-icon {
  font-size: 28px;
  display: block;
  margin-bottom: 8px;
}

.upload-tip {
  font-size: 12px;
  color: #999;
  margin-top: 8px;
  margin-bottom: 0;
}

.preview-container {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.preview-item {
  position: relative;
  width: 120px;
  height: 120px;
  border-radius: 4px;
  overflow: hidden;
  border: 1px solid #eee;
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.delete-button {
  position: absolute;
  top: 5px;
  right: 5px;
  width: 20px;
  height: 20px;
  background: rgba(0, 0, 0, 0.5);
  color: white;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 16px;
  line-height: 1;
  padding: 0;
}

.delete-button:hover {
  background: rgba(255, 0, 0, 0.7);
}
</style> 