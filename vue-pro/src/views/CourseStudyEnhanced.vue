<template>
  <!-- 增强版课程学习页：演示 Pinia 状态管理 -->
  <div class="course-study-enhanced-page">
    <!-- 顶部标题 -->
    <div class="page-header">
      <h1 class="page-title">课程学习（增强版）</h1>
      <p class="page-subtitle">课程 ID：{{ courseId }} · 演示 Pinia 状态管理</p>
    </div>

    <!-- 主体布局：左侧视频+进度+控制 / 右侧 AI 聊天 -->
    <el-row :gutter="20" class="main-row">
      <!-- 左侧：视频播放与学习进度 -->
      <el-col :span="14">
        <div class="left-panel">
          <!-- 视频播放占位区 -->
          <div class="video-placeholder">
            <i class="fa fa-play-circle play-icon"></i>
            <p class="placeholder-text">课程 {{ courseId }}</p>
            <p class="placeholder-sub">视频占位区</p>
          </div>

          <!-- 进度条区域 -->
          <div class="progress-area">
            <div class="progress-label">
              <span>学习进度</span>
              <span class="progress-percent">{{ courseStore.progressPercentage }}%</span>
            </div>
            <!-- 进度条：绑定百分比，禁用拖动 -->
            <el-slider
              v-model="courseStore.progressPercentage"
              :disabled="true"
              :show-tooltip="false"
            />
            <!-- 已学秒数 / 总秒数显示 -->
            <div class="time-info">
              <span>已学：{{ courseStore.learnedSeconds }} 秒</span>
              <span>总时长：{{ courseStore.totalSeconds }} 秒</span>
            </div>
          </div>

          <!-- 控制按钮区域 -->
          <div class="control-area">
            <el-button type="primary" @click="simulatePlay">
              <i class="fa fa-play"></i>
              模拟播放 5 秒
            </el-button>
            <span class="tip-text">点击按钮模拟视频播放，进度将自动推进</span>
          </div>
        </div>
      </el-col>

      <!-- 右侧：AI 聊天窗口 -->
      <el-col :span="10">
        <AIChatWindow :course-id="courseId" />
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
// 引入课程状态 store
import { useCourseStore } from '@/store/courseStore'
// 引入 AI 聊天窗口组件
import AIChatWindow from '@/components/AIChatWindow.vue'

// 路由实例，用于获取 courseId 参数
const route = useRoute()
// 从路由参数中取出 courseId
const courseId = ref<string>(String(route.params.courseId || route.params.id || ''))

// 课程 store 实例
const courseStore = useCourseStore()

/**
 * 模拟播放 5 秒：调用 store 更新进度
 */
function simulatePlay() {
  // 在当前已学秒数基础上加 5 秒
  const next = courseStore.learnedSeconds + 5
  courseStore.updateProgress(next)
}

// 组件挂载：初始化课程，模拟总时长 100 秒
onMounted(() => {
  courseStore.setCourse(courseId.value, 100)
})
</script>

<style scoped>
/* 页面根容器 */
.course-study-enhanced-page {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 24px;
}

/* 顶部标题区 */
.page-header {
  text-align: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 26px;
  color: #303133;
  margin: 0 0 8px 0;
}

.page-subtitle {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

/* 主体行 */
.main-row {
  max-width: 1400px;
  margin: 0 auto;
}

/* 左侧面板 */
.left-panel {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

/* 视频播放占位区，黑色背景，16:9 比例 */
.video-placeholder {
  width: 100%;
  aspect-ratio: 16 / 9;
  background: #000;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #fff;
  border-radius: 8px;
  margin-bottom: 20px;
}

.play-icon {
  font-size: 56px;
  color: #bfbfbf;
  margin-bottom: 12px;
}

.placeholder-text {
  font-size: 22px;
  font-weight: 600;
  margin: 0 0 6px 0;
}

.placeholder-sub {
  font-size: 13px;
  color: #8c8c8c;
  margin: 0;
}

/* 进度条区域 */
.progress-area {
  background: #fafafa;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 16px;
}

.progress-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  color: #303133;
  margin-bottom: 12px;
}

.progress-percent {
  color: #409eff;
  font-weight: 600;
}

.time-info {
  display: flex;
  justify-content: space-between;
  margin-top: 12px;
  font-size: 13px;
  color: #909399;
}

/* 控制按钮区域 */
.control-area {
  display: flex;
  align-items: center;
  gap: 12px;
}

.tip-text {
  font-size: 13px;
  color: #909399;
}
</style>
