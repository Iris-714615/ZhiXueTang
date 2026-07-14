// 直播间状态管理
import { defineStore } from 'pinia'
import { ref } from 'vue'

// 弹幕消息结构
export interface DanmakuMessage {
  id: string
  userId: string
  username: string
  content: string
  timestamp: number | string
  system?: boolean
  history?: boolean
}

export const useLiveStore = defineStore('live', () => {
  // 当前直播间 ID
  const roomId = ref<string>('')
  // WebSocket 是否已连接
  const isConnected = ref<boolean>(false)
  // 在线人数
  const onlineCount = ref<number>(0)
  // 弹幕列表
  const danmakuList = ref<DanmakuMessage[]>([])
  // 错误提示（限流等）
  const errorMessage = ref<string>('')

  /**
   * 设置当前直播间并清空弹幕
   */
  function setRoom(id: string) {
    roomId.value = id
    danmakuList.value = []
  }

  /**
   * 添加一条弹幕，最多保留最近 200 条
   */
  function addDanmaku(msg: DanmakuMessage) {
    danmakuList.value.push(msg)
    if (danmakuList.value.length > 200) {
      danmakuList.value = danmakuList.value.slice(-200)
    }
  }

  /**
   * 批量添加历史弹幕（去重）
   */
  function setHistory(messages: DanmakuMessage[]) {
    danmakuList.value = messages
  }

  /**
   * 设置连接状态
   */
  function setConnected(val: boolean) {
    isConnected.value = val
  }

  /**
   * 设置在线人数
   */
  function setOnlineCount(count: number) {
    onlineCount.value = count
  }

  /**
   * 显示错误提示，3 秒后自动清除
   */
  function setError(msg: string) {
    errorMessage.value = msg
    setTimeout(() => {
      if (errorMessage.value === msg) errorMessage.value = ''
    }, 3000)
  }

  return {
    roomId,
    isConnected,
    onlineCount,
    danmakuList,
    errorMessage,
    setRoom,
    addDanmaku,
    setHistory,
    setConnected,
    setOnlineCount,
    setError,
  }
})
