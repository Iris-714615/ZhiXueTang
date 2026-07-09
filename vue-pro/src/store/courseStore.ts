// 课程学习状态管理
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useCourseStore = defineStore('course', () => {
  // 当前课程 ID
  const currentCourseId = ref<string>('')
  // 已学习时长（秒）
  const learnedSeconds = ref<number>(0)
  // 课程总时长（秒），默认为 1 以避免除零
  const totalSeconds = ref<number>(1)

  // 学习进度百分比（0-100）
  const progressPercentage = computed(() => {
    return Math.min(100, Math.round((learnedSeconds.value / totalSeconds.value) * 100))
  })

  /**
   * 更新学习进度（仅前进不后退）
   * @param seconds 当前播放位置（秒）
   */
  function updateProgress(seconds: number) {
    if (seconds > learnedSeconds.value) {
      learnedSeconds.value = seconds
    }
  }

  /**
   * 设置当前课程并重置进度
   * @param courseId 课程 ID
   * @param total 课程总时长（秒）
   */
  function setCourse(courseId: string, total: number) {
    currentCourseId.value = courseId
    totalSeconds.value = total
    learnedSeconds.value = 0
  }

  return { currentCourseId, learnedSeconds, totalSeconds, progressPercentage, updateProgress, setCourse }
})
