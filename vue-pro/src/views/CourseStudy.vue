<template>
  <div class="course-study-page">
    <div class="course-study-container">
      <!-- 左侧视频和标题区域 -->
      <div class="main-content">
        <h1 class="course-title">{{ currentLesson?.title || '' }}</h1>

        <!-- 视频播放器 -->
        <div class="video-container">
          <video
              v-if="currentLesson?.lesson_type === 2"
              ref="videoPlayer"
              class="video-player"
              controls
              :src="currentLesson?.link"
              @timeupdate="handleTimeUpdate"
              @ended="handleVideoEnded"
          >
            您的浏览器不支持 HTML5 视频播放
          </video>
          <div v-else-if="currentLesson?.lesson_type === 1" class="exercise-container">
            <h3>练习内容</h3>
            <p>请前往练习系统完成练习：{{ currentLesson?.link }}</p>
          </div>
          <div v-else-if="currentLesson?.lesson_type === 0" class="doc-container">
            <h3>文档内容</h3>
            <p>请查看相关文档：{{ currentLesson?.link }}</p>
          </div>
        </div>
      </div>

      <!-- 右侧课程大纲 -->
      <div class="course-outline">
        <h2 class="outline-title">课程大纲</h2>

        <div class="chapter-list">
          <div
              v-for="chapter in courseContent"
              :key="chapter.id"
              class="chapter-item"
          >
            <div
                class="chapter-header"
                @click="toggleChapter(chapter.id)"
            >
              <i class="fas" :class="expandedChapters[chapter.id] ? 'fa-chevron-down' : 'fa-chevron-right'"></i>
              <span>第{{ chapter.number }}章：{{ chapter.title }}</span>
            </div>

            <div v-show="expandedChapters[chapter.id]" class="lesson-list">
              <div
                  v-for="lesson in chapter.lessons"
                  :key="lesson.id"
                  class="lesson-item"
                  :class="{
                  active: currentLesson?.id === lesson.id,
                  completed: completedLessons.includes(lesson.id)
                }"
                  @click="switchLesson(lesson)"
              >
                <div class="lesson-info">
                  <span class="lesson-title">
                    <i class="fas" :class="getLessonIcon(lesson.lesson_type)"></i>
                    {{ lesson.title }}
                  </span>
                  <span class="lesson-duration">{{ lesson.duration || '-' }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const videoPlayer = ref(null)

// 课程状态管理
const courseContent = ref([])
const currentLesson = ref(null)
const completedLessons = ref([])
const expandedChapters = ref({})

// 获取课程内容
const fetchCourseContent = async () => {
  try {
    const token = localStorage.getItem('token') || sessionStorage.getItem('token')
    const { courseId, orderNumber } = route.query

    if (!courseId || !orderNumber) {
      ElMessage.error('参数不完整')
      return
    }

    const response = await axios.get(
        `http://localhost:8000/courses/content/?order_number=${orderNumber}&course_id=${courseId}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
    )

    if (response.data.code === 1) {
      courseContent.value = response.data.data
      // 初始化章节展开状态
      courseContent.value.forEach(chapter => {
        expandedChapters.value[chapter.id] = chapter.id === courseContent.value[0].id
      })
      // 设置第一个课程为当前课程
      if (courseContent.value[0]?.lessons?.length > 0) {
        currentLesson.value = courseContent.value[0].lessons[0]
      }
    } else {
      throw new Error(response.data.message || '获取课程内容失败')
    }
  } catch (error) {
    console.error('获取课程内容失败:', error)
    ElMessage.error(error.message || '获取课程内容失败')
    router.push('/user')
  }
}

// 切换章节展开状态
const toggleChapter = (chapterId) => {
  expandedChapters.value[chapterId] = !expandedChapters.value[chapterId]
}

// 切换课程
const switchLesson = (lesson) => {
  currentLesson.value = lesson
}

// 获取课程类型图标
const getLessonIcon = (lessonType) => {
  switch (lessonType) {
    case 2: return 'fa-play-circle' // 视频
    case 1: return 'fa-tasks' // 练习
    case 0: return 'fa-file-alt' // 文档
    default: return 'fa-circle'
  }
}

// 处理视频播放进度
const handleTimeUpdate = () => {
  if (videoPlayer.value) {
    const progress = (videoPlayer.value.currentTime / videoPlayer.value.duration) * 100
    // 这里可以调用API保存播放进度
  }
}

// 处理视频播放完成
const handleVideoEnded = () => {
  if (!completedLessons.value.includes(currentLesson.value.id)) {
    completedLessons.value.push(currentLesson.value.id)
  }
  // 这里可以调用API更新课程完成状态
}

onMounted(() => {
  fetchCourseContent()
})
</script>

<style scoped>
.course-study-page {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.course-study-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
  display: flex;
  gap: 20px;
}

.main-content {
  flex: 1;
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.course-title {
  font-size: 24px;
  color: #333;
  margin: 0 0 20px 0;
}

.video-container {
  width: 100%;
  aspect-ratio: 16 / 9;
  background: #000;
  border-radius: 4px;
  overflow: hidden;
}

.video-player {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.exercise-container,
.doc-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background: #fff;
  color: #333;
  padding: 20px;
}

.course-outline {
  width: 300px;
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.outline-title {
  font-size: 18px;
  color: #333;
  margin: 0 0 20px 0;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.chapter-item {
  margin-bottom: 16px;
}

.chapter-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px;
  cursor: pointer;
  color: #333;
  font-weight: 500;
}

.chapter-header:hover {
  background: #f5f7fa;
  border-radius: 4px;
}

.lesson-list {
  margin-left: 24px;
}

.lesson-item {
  padding: 10px;
  cursor: pointer;
  border-radius: 4px;
  margin: 4px 0;
}

.lesson-item:hover {
  background: #f5f7fa;
}

.lesson-item.active {
  background: #e6f7ff;
  color: #1890ff;
}

.lesson-item.completed {
  color: #52c41a;
}

.lesson-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
}

.lesson-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.lesson-duration {
  color: #999;
  font-size: 12px;
}

@media (max-width: 1024px) {
  .course-study-container {
    flex-direction: column;
  }

  .course-outline {
    width: 100%;
  }
}

@media (max-width: 768px) {
  .course-study-container {
    padding: 10px;
  }

  .main-content {
    padding: 15px;
  }

  .course-title {
    font-size: 20px;
  }
}
</style>