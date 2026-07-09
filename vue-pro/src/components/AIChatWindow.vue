<template>
  <!-- AI 聊天窗口容器 -->
  <div class="ai-chat-window">
    <!-- 顶部标题栏：显示当前课程 ID -->
    <div class="chat-header">
      <span class="chat-title">AI 学习助手</span>
      <span class="course-id">当前课程：{{ courseId }}</span>
    </div>

    <!-- 消息列表区域，可滚动 -->
    <div class="message-list" ref="messageListRef">
      <!-- 空状态提示 -->
      <div v-if="chatStore.messages.length === 0" class="empty-tip">
        暂无消息，向 AI 提问开始学习吧～
      </div>

      <!-- 遍历消息列表，根据角色区分左右样式 -->
      <div
        v-for="(msg, index) in chatStore.messages"
        :key="index"
        class="message-row"
        :class="msg.role === 'user' ? 'is-user' : 'is-assistant'"
      >
        <div class="message-bubble" :class="msg.role === 'user' ? 'user-bubble' : 'assistant-bubble'">
          <!-- 用户消息直接渲染文本 -->
          <template v-if="msg.role === 'user'">{{ msg.content }}</template>
          <!-- AI 消息使用 Markdown 渲染 -->
          <div v-else class="markdown-body" v-html="renderMarkdown(msg.content)"></div>
        </div>
      </div>
    </div>

    <!-- 输入区域：输入框 + 发送按钮 -->
    <div class="input-area">
      <el-input
        v-model="inputMessage"
        type="textarea"
        :rows="2"
        placeholder="请输入你的问题，回车或点击发送按钮..."
        resize="none"
        @keydown.enter.exact.prevent="sendMessage"
      />
      <el-button
        type="primary"
        :loading="chatStore.isLoading"
        :disabled="!inputMessage.trim() || chatStore.isLoading"
        @click="sendMessage"
      >
        发送
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, watch } from 'vue'
// 引入 marked 库用于 Markdown 渲染
import { marked } from 'marked'
// 引入聊天状态 store
import { useChatStore } from '@/store/chatStore'
// 引入 AI 流式请求服务
import { fetchAIAssistantStream } from '@/services/aiService'

// 组件 props：课程 ID（必填），同时暴露给模板与脚本使用
const props = defineProps<{ courseId: string }>()

// 聊天 store 实例
const chatStore = useChatStore()

// 用户输入的消息内容
const inputMessage = ref<string>('')
// 消息列表容器的 ref，用于滚动控制
const messageListRef = ref<HTMLDivElement | null>(null)

/**
 * 将 Markdown 文本渲染为 HTML
 * @param text 原始 Markdown 文本
 * @returns 渲染后的 HTML 字符串
 */
function renderMarkdown(text: string): string {
  if (!text) return ''
  // 使用 marked 解析 Markdown，返回 HTML 字符串
  return marked.parse(text) as string
}

/**
 * 滚动消息列表到底部，展示最新消息
 */
function scrollToBottom() {
  nextTick(() => {
    if (messageListRef.value) {
      messageListRef.value.scrollTop = messageListRef.value.scrollHeight
    }
  })
}

/**
 * 发送消息：依次添加用户消息、AI 占位，再发起流式请求
 */
async function sendMessage() {
  const content = inputMessage.value.trim()
  // 输入为空或正在加载时不处理
  if (!content || chatStore.isLoading) return

  // 1. 添加用户消息到列表
  chatStore.addUserMessage(content)
  // 清空输入框
  inputMessage.value = ''
  // 滚动到底部
  scrollToBottom()

  // 2. 添加助手消息占位，并取得索引便于流式追加
  const placeholderIndex = chatStore.addAssistantPlaceholder()
  // 设置加载状态
  chatStore.setLoading(true)

  // 3. 发起流式请求，从 props 取出当前课程 ID
  await fetchAIAssistantStream(
    content,
    props.courseId,
    // onChunk：流式追加到助手消息
    (text: string) => {
      chatStore.updateAssistantMessage(placeholderIndex, text)
      scrollToBottom()
    },
    // onComplete：结束加载状态
    () => {
      chatStore.setLoading(false)
      scrollToBottom()
    },
    // onError：错误处理，将错误信息写入助手消息
    (error: any) => {
      chatStore.updateAssistantMessage(placeholderIndex, `\n\n[请求出错：${error?.message || error}]`)
      chatStore.setLoading(false)
      scrollToBottom()
    }
  )
}

// 监听消息列表长度变化，自动滚动到底部
watch(
  () => chatStore.messages.length,
  () => {
    scrollToBottom()
  }
)
</script>

<style scoped>
/* 聊天窗口整体容器，固定高度 600px */
.ai-chat-window {
  display: flex;
  flex-direction: column;
  height: 600px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

/* 顶部标题栏 */
.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: linear-gradient(135deg, #409eff, #66b1ff);
  color: #fff;
}

.chat-title {
  font-size: 16px;
  font-weight: 600;
}

.course-id {
  font-size: 12px;
  opacity: 0.9;
}

/* 消息列表区域，自动滚动 */
.message-list {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  background: #f5f7fa;
}

/* 空状态提示 */
.empty-tip {
  text-align: center;
  color: #999;
  font-size: 14px;
  padding: 40px 0;
}

/* 单条消息行，默认左对齐（AI 消息） */
.message-row {
  display: flex;
  margin-bottom: 12px;
}

/* 用户消息靠右 */
.message-row.is-user {
  justify-content: flex-end;
}

/* AI 消息靠左 */
.message-row.is-assistant {
  justify-content: flex-start;
}

/* 消息气泡通用样式 */
.message-bubble {
  max-width: 80%;
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.6;
  word-break: break-word;
}

/* 用户消息气泡：蓝色背景 */
.user-bubble {
  background: #409eff;
  color: #fff;
  border-top-right-radius: 4px;
}

/* AI 消息气泡：灰色背景 */
.assistant-bubble {
  background: #ffffff;
  color: #333;
  border: 1px solid #e4e7ed;
  border-top-left-radius: 4px;
}

/* Markdown 内容样式覆盖 */
.markdown-body :deep(p) {
  margin: 6px 0;
}

.markdown-body :deep(pre) {
  background: #2d2d2d;
  color: #f8f8f2;
  padding: 10px;
  border-radius: 6px;
  overflow-x: auto;
}

.markdown-body :deep(code) {
  font-family: Consolas, Monaco, monospace;
  font-size: 13px;
}

.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  padding-left: 20px;
  margin: 6px 0;
}

/* 输入区域 */
.input-area {
  display: flex;
  gap: 8px;
  padding: 12px;
  background: #fff;
  border-top: 1px solid #e4e7ed;
}

/* 输入框占满剩余空间 */
.input-area :deep(.el-textarea) {
  flex: 1;
}
</style>
