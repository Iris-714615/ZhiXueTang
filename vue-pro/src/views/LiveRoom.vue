<template>
  <!-- 直播间页面根容器，整体高度 800px -->
  <div class="live-room-page">
    <!-- 顶部信息栏：标题 + 在线人数 -->
    <div class="room-header">
      <div class="room-title">
        <span class="live-tag">LIVE</span>
        <span>直播间 {{ roomId }}</span>
      </div>
      <div class="online-info">
        <i class="fa fa-user"></i>
        在线人数：<span class="online-count">{{ liveStore.onlineCount }}</span>
      </div>
    </div>

    <!-- 主体布局：左侧视频区 + 右侧弹幕区 -->
    <div class="room-body">
      <!-- 左侧：视频播放占位区（16:9 比例，黑色背景） -->
      <div class="video-area">
        <div class="video-placeholder">
          <i class="fa fa-play-circle play-icon"></i>
          <p class="placeholder-text">直播间 {{ roomId }}</p>
          <p class="placeholder-sub">视频流加载中...</p>
        </div>
      </div>

      <!-- 右侧：弹幕区 -->
      <div class="danmaku-area">
        <div class="danmaku-header">
          <span>实时弹幕</span>
          <span class="conn-status" :class="{ connected: liveStore.isConnected }">
            {{ liveStore.isConnected ? '已连接' : '未连接' }}
          </span>
        </div>

        <!-- 弹幕列表，自动滚动到底部 -->
        <div class="danmaku-list" ref="danmakuListRef">
          <div v-if="liveStore.danmakuList.length === 0" class="danmaku-empty">
            暂无弹幕，快来发送第一条吧～
          </div>
          <div
            v-for="item in liveStore.danmakuList"
            :key="item.id"
            class="danmaku-item"
            :class="{ 'danmaku-system': item.system, 'danmaku-history': item.history }"
          >
            <span v-if="item.system" class="system-tag">系统</span>
            <span v-if="item.history" class="history-tag">历史</span>
            <span class="danmaku-user" :class="{ 'user-system': item.system }">{{ item.username }}：</span>
            <span class="danmaku-content">{{ item.content }}</span>
          </div>
        </div>

        <!-- 错误提示条 -->
        <div v-if="liveStore.errorMessage" class="danmaku-error-tip">
          {{ liveStore.errorMessage }}
        </div>

        <!-- 弹幕输入区 -->
        <div class="danmaku-input">
          <el-input
            v-model="danmakuContent"
            placeholder="发条弹幕吧..."
            maxlength="100"
            show-word-limit
            @keydown.enter="sendDanmaku"
          />
          <el-button type="primary" @click="sendDanmaku" :disabled="!danmakuContent.trim()">
            发送
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
// 引入直播间 WebSocket 服务
import { LiveRoomWebSocket } from '@/services/websocketService'
// 引入直播间状态 store
import { useLiveStore } from '@/store/liveStore'

// 路由实例，获取 roomId 路由参数
const route = useRoute()
// 从路由参数中取出 roomId
const roomId = ref<string>(String(route.params.roomId || ''))

// 从 localStorage 读取登录用户名
const currentUsername = ref<string>(localStorage.getItem('username') || '匿名用户')

// 直播间 store 实例
const liveStore = useLiveStore()

// WebSocket 实例引用
let ws: LiveRoomWebSocket | null = null

// 弹幕输入内容
const danmakuContent = ref<string>('')
// 弹幕列表容器 ref，用于滚动控制
const danmakuListRef = ref<HTMLDivElement | null>(null)

/**
 * WebSocket 消息回调，根据消息类型分发处理
 */
function onMessage(data: any) {
  if (!data || !data.type) return
  switch (data.type) {
    case 'danmaku':
      // 弹幕消息：添加到 store
      liveStore.addDanmaku({
        id: `${data.timestamp}-${Math.random().toString(36).slice(2, 8)}`,
        userId: data.user_id || data.userId || '',
        username: data.username || '匿名用户',
        content: data.content || '',
        timestamp: data.timestamp || Date.now(),
        system: data.system || false,
        history: data.history || false,
      })
      scrollToBottom()
      break
    case 'online_count':
      // 在线人数更新
      liveStore.setOnlineCount(Number(data.online_count || data.count || 0))
      break
    case 'error':
      // 限流等错误提示
      liveStore.setError(data.message || '发送失败')
      break
    case 'pong':
    case 'heartbeat':
      // 心跳响应，无需处理
      break
    default:
      break
  }
}

/**
 * 滚动弹幕列表到底部
 */
function scrollToBottom() {
  nextTick(() => {
    if (danmakuListRef.value) {
      danmakuListRef.value.scrollTop = danmakuListRef.value.scrollHeight
    }
  })
}

/**
 * 发送弹幕：通过 WebSocket 发送
 * 注意：服务端会广播回来，本地不再手动添加，避免重复
 */
function sendDanmaku() {
  const content = danmakuContent.value.trim()
  if (!content || !ws) return

  ws.sendDanmaku(content)
  danmakuContent.value = ''
  scrollToBottom()
}

// 监听弹幕列表长度变化，自动滚动到底部
watch(
  () => liveStore.danmakuList.length,
  () => {
    scrollToBottom()
  }
)

// 组件挂载：初始化 WebSocket 连接
onMounted(() => {
  liveStore.setRoom(roomId.value)
  // 传入当前用户名，便于服务端识别
  ws = new LiveRoomWebSocket(roomId.value, onMessage, currentUsername.value)
  ws.connect()
  liveStore.setConnected(true)
})

// 组件卸载：断开 WebSocket 连接
onUnmounted(() => {
  if (ws) {
    ws.disconnect()
    ws = null
  }
  liveStore.setConnected(false)
})
</script>

<style scoped>
/* 页面根容器，整体高度 800px */
.live-room-page {
  height: 800px;
  display: flex;
  flex-direction: column;
  background: #1f1f1f;
  color: #fff;
  border-radius: 12px;
  overflow: hidden;
  margin: 20px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
}

/* 顶部信息栏 */
.room-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: #141414;
  border-bottom: 1px solid #303030;
}

.room-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: 600;
}

.live-tag {
  background: #ff4d4f;
  color: #fff;
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 600;
  letter-spacing: 1px;
}

.online-info {
  font-size: 14px;
  color: #bfbfbf;
}

.online-info .fa {
  margin-right: 4px;
}

.online-count {
  color: #52c41a;
  font-weight: 600;
  margin: 0 4px;
}

/* 主体布局：左侧视频 + 右侧弹幕 */
.room-body {
  flex: 1;
  display: flex;
  overflow: hidden;
}

/* 左侧视频区域 */
.video-area {
  flex: 1;
  background: #000;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 视频占位区，保持 16:9 比例 */
.video-placeholder {
  width: 90%;
  aspect-ratio: 16 / 9;
  background: #000;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #fff;
  border: 1px solid #303030;
  border-radius: 8px;
}

.play-icon {
  font-size: 64px;
  color: #bfbfbf;
  margin-bottom: 16px;
}

.placeholder-text {
  font-size: 24px;
  font-weight: 600;
  margin: 0 0 8px 0;
}

.placeholder-sub {
  font-size: 14px;
  color: #8c8c8c;
  margin: 0;
}

/* 右侧弹幕区域 */
.danmaku-area {
  width: 360px;
  background: #fff;
  color: #303133;
  display: flex;
  flex-direction: column;
  border-left: 1px solid #e4e7ed;
}

.danmaku-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #ebeef5;
  font-size: 14px;
  font-weight: 600;
}

.conn-status {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 10px;
  background: #f5f5f5;
  color: #999;
}

.conn-status.connected {
  background: #f6ffed;
  color: #52c41a;
  border: 1px solid #b7eb8f;
}

/* 弹幕列表，自动滚动 */
.danmaku-list {
  flex: 1;
  overflow-y: auto;
  padding: 12px 16px;
  background: #fafafa;
}

.danmaku-empty {
  text-align: center;
  color: #c0c4cc;
  font-size: 13px;
  padding: 40px 0;
}

.danmaku-item {
  padding: 8px 10px;
  margin-bottom: 6px;
  background: #fff;
  border-radius: 6px;
  font-size: 13px;
  line-height: 1.5;
  word-break: break-word;
  border: 1px solid #f0f0f0;
}

.danmaku-item.danmaku-system {
  background: #fffbe6;
  border-color: #ffe58f;
  color: #8c8c8c;
  font-style: italic;
}

.danmaku-item.danmaku-history {
  opacity: 0.75;
}

.system-tag,
.history-tag {
  display: inline-block;
  font-size: 10px;
  padding: 1px 5px;
  border-radius: 3px;
  margin-right: 4px;
  font-style: normal;
  font-weight: 600;
}

.system-tag {
  background: #faad14;
  color: #fff;
}

.history-tag {
  background: #d9d9d9;
  color: #595959;
}

.danmaku-user {
  color: #409eff;
  font-weight: 600;
  margin-right: 4px;
}

.danmaku-user.user-system {
  color: #faad14;
}

.danmaku-content {
  color: #303133;
}

/* 错误提示条 */
.danmaku-error-tip {
  background: #fff1f0;
  color: #cf1322;
  font-size: 12px;
  padding: 6px 16px;
  border-top: 1px solid #ffa39e;
  text-align: center;
}

/* 弹幕输入区 */
.danmaku-input {
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  border-top: 1px solid #ebeef5;
  background: #fff;
}
</style>
