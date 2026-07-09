// AI 聊天状态管理
import { defineStore } from 'pinia'
import { ref } from 'vue'

// 聊天消息结构
export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp?: number
}

export const useChatStore = defineStore('chat', () => {
  // 消息列表
  const messages = ref<ChatMessage[]>([])
  // 是否正在等待 AI 响应
  const isLoading = ref<boolean>(false)
  // 当前关联的课程 ID
  const currentCourseId = ref<string>('')

  /**
   * 添加用户消息
   * @param content 用户输入内容
   */
  function addUserMessage(content: string) {
    messages.value.push({ role: 'user', content, timestamp: Date.now() })
  }

  /**
   * 添加助手消息占位（空内容），返回其索引便于后续追加
   * @returns 占位消息在列表中的索引
   */
  function addAssistantPlaceholder() {
    messages.value.push({ role: 'assistant', content: '', timestamp: Date.now() })
    return messages.value.length - 1
  }

  /**
   * 追加更新助手消息内容（用于流式响应）
   * @param index 消息索引
   * @param content 本次追加的文本
   */
  function updateAssistantMessage(index: number, content: string) {
    if (index >= 0 && index < messages.value.length) {
      const target = messages.value[index]
      if (target) {
        target.content += content
      }
    }
  }

  /**
   * 设置加载状态
   * @param val 是否加载中
   */
  function setLoading(val: boolean) {
    isLoading.value = val
  }

  /**
   * 清空所有消息
   */
  function clearMessages() {
    messages.value = []
  }

  /**
   * 设置当前课程并清空历史消息
   * @param courseId 课程 ID
   */
  function setCourse(courseId: string) {
    currentCourseId.value = courseId
    messages.value = []
  }

  return { messages, isLoading, currentCourseId, addUserMessage, addAssistantPlaceholder, updateAssistantMessage, setLoading, clearMessages, setCourse }
})
