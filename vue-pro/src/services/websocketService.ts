// WebSocket 服务，用于直播间实时互动
const WS_BASE = 'ws://localhost:8000'

export class LiveRoomWebSocket {
  private ws: WebSocket | null = null
  private roomId: string
  private onMessage: (data: any) => void
  private heartbeatTimer: number | null = null

  constructor(roomId: string, onMessage: (data: any) => void) {
    this.roomId = roomId
    this.onMessage = onMessage
  }

  /**
   * 建立 WebSocket 连接
   */
  connect() {
    // 创建 WebSocket 连接到直播间地址
    this.ws = new WebSocket(`${WS_BASE}/ws/live/${this.roomId}/`)

    // 连接成功时启动心跳
    this.ws.onopen = () => {
      console.log(`WebSocket 已连接到直播间 ${this.roomId}`)
      this.startHeartbeat()
    }

    // 接收到消息时解析 JSON 并回调
    this.ws.onmessage = (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data)
        this.onMessage(data)
      } catch {
        // 非 JSON 数据，直接作为原始数据回调
        this.onMessage(event.data)
      }
    }

    // 连接关闭时清理心跳
    this.ws.onclose = () => {
      console.log('WebSocket 连接已关闭')
      this.stopHeartbeat()
    }

    // 发生错误时打印日志
    this.ws.onerror = (error: Event) => {
      console.error('WebSocket 发生错误：', error)
    }
  }

  /**
   * 发送数据
   * @param data 要发送的数据对象
   */
  send(data: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
    } else {
      console.warn('WebSocket 未连接，无法发送数据')
    }
  }

  /**
   * 发送弹幕消息
   * @param content 弹幕内容
   */
  sendDanmaku(content: string) {
    this.send({ type: 'danmaku', content, timestamp: Date.now() })
  }

  /**
   * 断开连接
   */
  disconnect() {
    this.stopHeartbeat()
    if (this.ws) {
      // 移除 onclose 回调，避免主动关闭时触发清理逻辑
      this.ws.onclose = null
      this.ws.close()
      this.ws = null
    }
  }

  /**
   * 启动心跳定时器（每 25 秒发送一次 ping）
   */
  private startHeartbeat() {
    this.heartbeatTimer = window.setInterval(() => {
      this.send({ type: 'ping' })
    }, 25000)
  }

  /**
   * 停止心跳定时器
   */
  private stopHeartbeat() {
    if (this.heartbeatTimer !== null) {
      clearInterval(this.heartbeatTimer)
      this.heartbeatTimer = null
    }
  }
}
