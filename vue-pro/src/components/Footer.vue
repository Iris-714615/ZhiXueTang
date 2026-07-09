<template>
  <footer class="site-footer">
    <div class="footer-inner">
      <div class="footer-links">
        <a href="#">关于知乎知学堂</a>
        <a href="#">联系我们</a>
        <a href="#">加入我们</a>
        <a href="#">用户协议</a>
        <a href="#">隐私政策</a>
        <a href="#">帮助中心</a>
      </div>
      <div class="footer-bottom">
        <span>© 2026 知乎知学堂 保留所有权利</span>
        <span class="footer-icp">京ICP备XXXXXXXX号</span>
      </div>
    </div>
  </footer>
</template>

<script setup>
</script>

<style scoped>
.site-footer {
  background: #f6f6f6;
  border-top: 1px solid #ebebeb;
  padding: 32px 0 24px;
  margin-top: 48px;
}

.footer-inner {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
  text-align: center;
}

.footer-links {
  margin-bottom: 16px;
}

.footer-links a {
  margin: 0 12px;
  color: #8590a6;
  text-decoration: none;
  font-size: 13px;
  transition: color 0.2s;
}

.footer-links a:hover {
  color: #1a1a1a;
}

.footer-bottom {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  color: #b4b4b4;
  font-size: 12px;
}

.footer-icp {
  font-size: 12px;
}
</style>
