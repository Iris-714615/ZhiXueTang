// 直播间状态管理
import { defineStore } from 'pinia'
import { ref } from 'vue'

// 弹幕消息结构
export interface DanmakuMessage {
  id: string
  userId: string
  username: string
  content: string
  timestamp: number
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

  /**
   * 设置当前直播间并清空弹幕
   * @param id 直播间 ID
   */
  function setRoom(id: string) {
    roomId.value = id
    danmakuList.value = []
  }

  /**
   * 添加一条弹幕，最多保留最近 200 条
   * @param msg 弹幕消息
   */
  function addDanmaku(msg: DanmakuMessage) {
    danmakuList.value.push(msg)
    // 超过 200 条时只保留最近 200 条
    if (danmakuList.value.length > 200) {
      danmakuList.value = danmakuList.value.slice(-200)
    }
  }

  /**
   * 设置连接状态
   * @param val 是否已连接
   */
  function setConnected(val: boolean) {
    isConnected.value = val
  }

  /**
   * 设置在线人数
   * @param count 在线人数
   */
  function setOnlineCount(count: number) {
    onlineCount.value = count
  }

  return { roomId, isConnected, onlineCount, danmakuList, setRoom, addDanmaku, setConnected, setOnlineCount }
})
