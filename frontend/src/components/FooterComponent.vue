<template>
  <footer class="site-footer">
    <div class="footer-content">
      <p>© {{ new Date().getFullYear() }} Two手交易平台 | All Rights Reserved</p>
      <div class="footer-links">
        <a href="#">关于我们</a>
        <a href="#">使用条款</a>
        <a href="#">隐私政策</a>
        <a href="#">联系我们</a>
      </div>
    </div>
  </footer>
</template>

<script setup>
// 页脚组件不需要太多逻辑
</script>

<style scoped>
.site-footer {
  text-align: center;
  padding: 20px 0;
  background-color: #f9f9f9;
  border-top: 1px solid #eee;
  margin-top: 20px;
  color: #666;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.footer-links {
  margin-top: 10px;
}

.footer-links a {
  margin: 0 10px;
  color: #666;
  text-decoration: none;
}

.footer-links a:hover {
  color: #409EFF;
  text-decoration: underline;
}
</style> 