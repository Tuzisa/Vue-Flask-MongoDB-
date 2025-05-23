<template>
  <div class="purchase-page-container">
    <el-card class="purchase-card">
      <template #header>
        <div class="card-header">
          <h2>确认订单</h2>
          <el-button @click="$router.go(-1)" text bg>返回商品</el-button>
        </div>
      </template>

      <div v-if="loading" class="loading-state">
        <el-skeleton :rows="5" animated />
      </div>

      <div v-if="item && !loading" class="order-details">
        <el-row :gutter="20">
          <el-col :span="8">
            <img :src="item.images && item.images.length > 0 ? item.images[0] : '/placeholder-image.png'" alt="商品图片" class="item-image" />
          </el-col>
          <el-col :span="16">
            <h3>{{ item.title }}</h3>
            <p class="item-price">价格: ¥{{ item.price?.toFixed(2) }}</p>
            <el-form label-width="100px">
              <el-form-item label="购买数量">
                <el-input-number v-model="quantity" :min="1" :max="item.stock || 10" />
              </el-form-item>
            </el-form>
          </el-col>
        </el-row>

        <el-divider />

        <h4>收货地址</h4>
        <el-form :model="addressForm" label-position="top">
          <el-form-item label="收货人姓名">
            <el-input v-model="addressForm.name" placeholder="请输入姓名"></el-input>
          </el-form-item>
          <el-form-item label="手机号码">
            <el-input v-model="addressForm.phone" placeholder="请输入手机号"></el-input>
          </el-form-item>
          <el-form-item label="详细地址">
            <el-input type="textarea" v-model="addressForm.address" placeholder="请输入详细地址"></el-input>
          </el-form-item>
        </el-form>

        <el-divider />

        <h4>支付方式</h4>
        <el-radio-group v-model="paymentMethod">
          <el-radio label="alipay">支付宝</el-radio>
          <el-radio label="wechatpay">微信支付</el-radio>
          <el-radio label="card">银行卡</el-radio>
        </el-radio-group>

        <div class="order-summary">
          <p>商品总价: ¥{{ (item.price * quantity).toFixed(2) }}</p>
          <p>运费: ¥0.00</p>
          <h3>应付总额: ¥{{ (item.price * quantity).toFixed(2) }}</h3>
        </div>

        <el-button type="danger" size="large" class="submit-order-btn" @click="submitOrder" :loading="submitting">
          提交订单
        </el-button>
      </div>
      <el-empty v-if="!item && !loading" description="无法加载商品信息"></el-empty>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useItemStore } from '@/stores/item';
import { ElMessage } from 'element-plus';

const route = useRoute();
const router = useRouter();
const itemStore = useItemStore();

const item = ref(null);
const loading = ref(true);
const submitting = ref(false);
const quantity = ref(1);
const paymentMethod = ref('alipay');

const addressForm = ref({
  name: '测试用户',
  phone: '13800138000',
  address: '北京市海淀区模拟街道123号'
});

onMounted(async () => {
  const itemId = route.params.itemId;
  if (!itemId) {
    ElMessage.error('无效的商品ID');
    router.push('/items');
    return;
  }
  try {
    item.value = await itemStore.fetchItemById(itemId);
  } catch (error) {
    console.error('获取商品信息失败:', error);
    ElMessage.error('无法加载商品信息');
  } finally {
    loading.value = false;
  }
});

const submitOrder = () => {
  submitting.value = true;
  ElMessage.info('正在提交订单 (模拟操作)');
  setTimeout(() => {
    submitting.value = false;
    ElMessage.success('订单提交成功 (模拟)!');
    router.push('/'); // 跳转到首页或订单成功页
  }, 2000);
};

</script>

<style scoped>
.purchase-page-container {
  max-width: 800px;
  margin: 20px auto;
}

.purchase-card {
  border-radius: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  font-size: 1.5rem;
}

.item-image {
  width: 100%;
  max-height: 200px;
  object-fit: cover;
  border-radius: 6px;
  margin-bottom: 10px;
}

.item-price {
  font-size: 1.2rem;
  color: #F56C6C;
  margin-bottom: 15px;
}

.el-divider {
  margin: 25px 0;
}

.order-summary {
  margin-top: 25px;
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 6px;
}

.order-summary p {
  margin: 5px 0;
}

.order-summary h3 {
  margin-top: 10px;
  color: #F56C6C;
}

.submit-order-btn {
  width: 100%;
  margin-top: 25px;
}

.loading-state {
  padding: 20px;
}
</style> 