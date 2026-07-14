// WebSocket 服务，用于直播间实时互动
const WS_BASE = 'ws://localhost:8000'

export class LiveRoomWebSocket {
  private ws: WebSocket | null = null
  private roomId: string
  private username: string
  private onMessage: (data: any) => void
  private heartbeatTimer: number | null = null
  private reconnectTimer: number | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private isManualClose = false

  constructor(roomId: string, onMessage: (data: any) => void, username = '匿名用户') {
    this.roomId = roomId
    this.onMessage = onMessage
    this.username = username
  }

  /**
   * 建立 WebSocket 连接
   */
  connect() {
    this.isManualClose = false
    // 将 username 作为 query string 传递给后端
    const encodedName = encodeURIComponent(this.username)
    this.ws = new WebSocket(`${WS_BASE}/ws/live/${this.roomId}/?username=${encodedName}`)

    // 连接成功时启动心跳
    this.ws.onopen = () => {
      console.log(`WebSocket 已连接到直播间 ${this.roomId}`)
      this.reconnectAttempts = 0
      this.startHeartbeat()
    }

    // 接收到消息时解析 JSON 并回调
    this.ws.onmessage = (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data)
        this.onMessage(data)
      } catch {
        this.onMessage(event.data)
      }
    }

    // 连接关闭时清理心跳并尝试重连
    this.ws.onclose = () => {
      console.log('WebSocket 连接已关闭')
      this.stopHeartbeat()
      if (!this.isManualClose) {
        this.tryReconnect()
      }
    }

    // 发生错误时打印日志
    this.ws.onerror = (error: Event) => {
      console.error('WebSocket 发生错误：', error)
    }
  }

  /**
   * 断线重连：指数退避（1s/2s/4s/8s/16s）
   */
  private tryReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.warn('重连次数已达上限，停止重连')
      return
    }
    this.reconnectAttempts++
    const delay = Math.pow(2, this.reconnectAttempts - 1) * 1000
    console.log(`第 ${this.reconnectAttempts} 次重连，${delay}ms 后尝试...`)
    this.reconnectTimer = window.setTimeout(() => {
      this.connect()
    }, delay)
  }

  /**
   * 发送数据
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
   */
  sendDanmaku(content: string) {
    this.send({ type: 'danmaku', content, timestamp: Date.now() })
  }

  /**
   * 主动断开连接（不触发重连）
   */
  disconnect() {
    this.isManualClose = true
    this.stopHeartbeat()
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
    if (this.ws) {
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
