<template>
  <!-- AI 伴学助手页面根容器 -->
  <div class="ai-assistant-page">
    <!-- 顶部页面标题 -->
    <div class="page-header">
      <h1 class="page-title">知学堂 AI 伴学助手</h1>
      <p class="page-subtitle">选择课程，与 AI 一起高效学习</p>
    </div>

    <!-- 主体布局：左侧课程选择 + 右侧聊天窗口 -->
    <el-row :gutter="20" class="main-row">
      <!-- 左侧：课程选择 -->
      <el-col :span="6">
        <div class="course-panel">
          <h3 class="panel-title">选择课程</h3>
          <!-- 课程下拉选择，绑定到 selectedCourseId -->
          <el-select
            v-model="selectedCourseId"
            placeholder="请选择课程"
            style="width: 100%"
            @change="handleCourseChange"
          >
            <el-option
              v-for="course in courseList"
              :key="course.id"
              :label="course.name"
              :value="course.id"
            />
          </el-select>

          <!-- 课程列表说明 -->
          <ul class="course-tips">
            <li v-for="course in courseList" :key="course.id" :class="{ active: course.id === selectedCourseId }">
              <span class="tip-id">{{ course.id }}</span>
              <span class="tip-name">{{ course.name }}</span>
            </li>
          </ul>
        </div>
      </el-col>

      <!-- 右侧：聊天窗口 -->
      <el-col :span="18">
        <AIChatWindow :course-id="selectedCourseId" />
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
// 引入 AI 聊天窗口组件
import AIChatWindow from '@/components/AIChatWindow.vue'
// 引入聊天状态 store
import { useChatStore } from '@/store/chatStore'

// 聊天 store 实例
const chatStore = useChatStore()

// 课程列表（硬编码 3 个示例课程）
const courseList = ref([
  { id: 'course_1', name: 'Vue3 实战' },
  { id: 'course_2', name: 'Go 微服务' },
  { id: 'course_3', name: 'Python AI' }
])

// 当前选中的课程 ID，默认选择第一个
const selectedCourseId = ref<string>('course_1')

/**
 * 课程切换处理：同步到 chatStore，重置该课程历史消息
 * @param courseId 选中的课程 ID
 */
function handleCourseChange(courseId: string) {
  chatStore.setCourse(courseId)
}
</script>

<style scoped>
/* 页面根容器 */
.ai-assistant-page {
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
  font-size: 28px;
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
  max-width: 1200px;
  margin: 0 auto;
}

/* 左侧课程面板 */
.course-panel {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.panel-title {
  font-size: 16px;
  color: #303133;
  margin: 0 0 16px 0;
  padding-bottom: 10px;
  border-bottom: 1px solid #ebeef5;
}

/* 课程说明列表 */
.course-tips {
  list-style: none;
  padding: 0;
  margin: 16px 0 0 0;
}

.course-tips li {
  display: flex;
  justify-content: space-between;
  padding: 8px 10px;
  border-radius: 6px;
  font-size: 14px;
  color: #606266;
  margin-bottom: 6px;
  background: #f5f7fa;
  transition: all 0.2s;
}

.course-tips li.active {
  background: #ecf5ff;
  color: #409eff;
  font-weight: 600;
}

.tip-id {
  color: #909399;
  font-family: Consolas, Monaco, monospace;
  font-size: 12px;
}

.course-tips li.active .tip-id {
  color: #409eff;
}

.tip-name {
  flex: 1;
  text-align: right;
}
</style>
