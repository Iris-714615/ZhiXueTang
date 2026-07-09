<template>
  <div class="float-toolbar">
    <div class="toolbar-item" @click="goToAIAssistant" title="AI工具">
      <div class="toolbar-icon">
        <i class="fas fa-robot"></i>
      </div>
      <span>AI工具</span>
    </div>
    <div class="toolbar-item" title="免费资料">
      <div class="toolbar-icon">
        <i class="fas fa-folder-open"></i>
      </div>
      <span>免费资料</span>
    </div>
    <div class="toolbar-item" title="APP下载">
      <div class="toolbar-icon">
        <i class="fas fa-mobile-alt"></i>
      </div>
      <span>APP下载</span>
    </div>
    <div class="toolbar-item" title="关注我们">
      <div class="toolbar-icon">
        <i class="fas fa-qrcode"></i>
      </div>
      <span>关注我们</span>
    </div>
    <div class="toolbar-item" @click="scrollToTop" title="回到顶部">
      <div class="toolbar-icon">
        <i class="fas fa-chevron-up"></i>
      </div>
      <span>回到顶部</span>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goToAIAssistant = () => {
  router.push('/ai-assistant')
}

const scrollToTop = () => {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
</script>

<style scoped>
.float-toolbar {
  position: fixed;
  right: 24px;
  top: 50%;
  transform: translateY(-50%);
  z-index: 999;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.toolbar-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px 8px;
  background: #fff;
  border: 1px solid #ebebeb;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  min-width: 56px;
}

.toolbar-item:hover {
  background: #f6f6f6;
  border-color: #0066ff;
}

.toolbar-icon {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 4px;
  color: #0066ff;
  font-size: 16px;
}

.toolbar-item span {
  font-size: 11px;
  color: #8590a6;
  white-space: nowrap;
}
</style>
