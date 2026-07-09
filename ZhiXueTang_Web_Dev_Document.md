# 知乎知学堂（微服务与 AGI 混合架构）Web 端开发设计文档

## 一、 引言与设计概述
本工程开发设计文档针对“知乎知学堂”职业教育平台的 Web 端及相关 AI 协同模块进行全方位架构与开发细节拆解。

### 1.1 系统架构演进核心思想
为了兼顾“大流量、高并发的核心教务与电商系统”以及“快速迭代、高度灵活的 AGI 伴学与智能问答系统”，本方案摒弃传统的单一语言技术栈，采用 **Golang (核心业务) + Python (AI 智能体) 双引擎混合微服务架构**。
*   **前端（Vue 3 生态）**：采用全组合式 API（Composition API），使用 TypeScript 保证类型安全，引入 Pinia 作为跨组件状态管理中心，支持 WebSocket 实现直播互动弹幕及大模型 SSE（Server-Sent Events）流式响应。
*   **后端（核心业务 - Golang）**：由 Go (如 Gin / Gofiber) 承载用户、选课、支付、课程权益、学习进度等强 I/O 密集、高并发业务，原生 Goroutine 协程机制保障万级 QPS 下的极低时延与资源开销。
*   **后端（AI 交互 - Python FastAPI）**：利用 Python 极其成熟的 AGI 生态（LangChain, LangGraph, LlamaIndex），基于 FastAPI 的异步原生架构，构建轻量级且高性能的智能伴学与知识库检索（RAG）微服务。

---

## 二、 关键技术栈清单与角色定位

| 技术/组件 | 技术选型与版本 | 在系统中的角色定位 |
| :--- | :--- | :--- |
| **前端框架** | Vue 3 + Vite + TS | 平台 Web 端 SPA 架构、组件化 UI 渲染与复杂流式交互 |
| **主业务后端** | Golang (Go 1.21+) | 用户、支付、选课、学习记录等高并发核心业务微服务 |
| **AI 业务后端** | Python 3.11 + FastAPI | AGI 伴学、智能问答、文档向量化处理等异步 AI 微服务 |
| **主关系型 DB** | MySQL 8.0 | 选课、订单、流水、班级关系等高 ACID 事务数据存储 |
| **高速缓存/锁** | Redis 7.0 | 用户 Session 共享、直播间热点数据、接口防刷分布式锁 |
| **搜索引擎/向量库**| Elasticsearch 8.x | 站内课程多维检索、课程文档/字幕向量化语义搜索（RAG） |
| **异步任务队列** | Celery + Redis | 课程文档 OCR 异步解析、大批量音视频字幕提取、离线数据报表 |
| **实时通信** | WebSocket / SSE | 直播间实时互动、连麦信令、AI 问答逐字流式打字效果 |
| **身份认证体系** | JWT (无状态 Bearer Token) | 微服务间跨域、跨语言统一鉴权，解耦网关与业务服务 |
| **AI 开发编排** | LangChain / LangGraph / LlamaIndex | 智能体决策流图构建、上下文多轮会话记忆、本地企业知识库构建 |

---

## 三、 前端架构与开发细节 (Vue 3 + TS)

### 3.1 流式响应（Streaming）与 SSE 渲染
在 AI 伴学助手模块，LLM 返回的数据为流式文本。为了让学员获得流畅的“逐字弹出”交互，前端使用原生 `ReadableStream` 配合 `fetch` API 建立长连接：

```typescript
// src/services/aiService.ts
export async function fetchAIAssistantStream(
  prompt: string, 
  onChunk: (text: string) => void,
  onComplete: () => void
) {
  const response = await fetch('/api/v1/ai/assistant/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    },
    body: JSON.stringify({ prompt })
  });

  if (!response.body) return;
  const reader = response.body.getReader();
  const decoder = new TextDecoder('utf-8');

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    const chunkText = decoder.decode(value, { stream: true });
    onChunk(chunkText);
  }
  onComplete();
}
```

在 Vue 3 组件中，使用 `ref` 维护对话队列，利用 `v-html` 或结合 `marked` 库实时解析 Markdown 语法：

```vue
<!-- src/components/AIChatWindow.vue -->
<script setup lang="ts">
import { ref } from 'vue';
import { marked } from 'marked';
import { fetchAIAssistantStream } from '../services/aiService';

const inputMessage = ref('');
const messages = ref<{ role: 'user' | 'assistant', content: string }[]>([]);

const sendMessage = async () => {
  if (!inputMessage.value.trim()) return;
  
  // 插入用户消息
  messages.value.push({ role: 'user', content: inputMessage.value });
  const userPrompt = inputMessage.value;
  inputMessage.value = '';

  // 预插入 AI 占位节点
  messages.value.push({ role: 'assistant', content: '' });
  const aiMessageIndex = messages.value.length - 1;

  await fetchAIAssistantStream(
    userPrompt,
    (chunk) => {
      // 实时追加字符并触发响应式更新
      messages.value[aiMessageIndex].content += chunk;
    },
    () => {
      console.log('AI Response streaming completed.');
    }
  );
};
</script>

<template>
  <div class="chat-container">
    <div v-for="(msg, idx) in messages" :key="idx" :class="['message', msg.role]">
      <div v-html="marked.parse(msg.content)"></div>
    </div>
    <div class="input-area">
      <input v-model="inputMessage" @keyup.enter="sendMessage" placeholder="向知学堂 AI 助手提问..." />
      <button @click="sendMessage">发送</button>
    </div>
  </div>
</template>
```

### 3.2 跨组件状态管理与双向通信 (Pinia)
教务系统涉及多个顶层组件（侧边栏、顶部选课、视频播放器、已学进度条）的数据同步。利用 Pinia 统一调度：

```typescript
// src/store/courseStore.ts
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export const useCourseStore = defineStore('course', () => {
  const currentCourseId = ref<string>('');
  const learnedSeconds = ref<number>(0);
  const totalSeconds = ref<number>(1);

  const progressPercentage = computed(() => {
    return Math.min(100, Math.round((learnedSeconds.value / totalSeconds.value) * 100));
  });

  function updateProgress(seconds: number) {
    if (seconds > learnedSeconds.value) {
      learnedSeconds.value = seconds;
    }
  }

  return { currentCourseId, learnedSeconds, totalSeconds, progressPercentage, updateProgress };
});
```

---

## 四、 后端混合微服务架构设计

```
                      +-------------------+
                      |   Vue 3 Client    |
                      +---------+---------+
                                |  (HTTP / WebSocket / SSE)
                                v
                      +-------------------+
                      |   Kong / APISIX   |  (API Gateway)
                      +----+---------+----+
                           |         |
      +--------------------+         +--------------------+
      | (JWT Validation & High QPS)                       | (Async AI & RAG)
      v                                                   v
+-----+-----------------------+                     +-----+-----------------------+
|    Golang Core Microservice |                     |   Python FastAPI Service    |
|   (Gin / Gofiber)           |                     |   (asyncio Engine)          |
+-----+--------------+--------+                     +-----+--------------+--------+
      |              |                                    |              |
      v              v                                    v              v
  +---+---+      +---+---+                            +---+---+      +---+---+
  | MySQL |      | Redis |                            |  ES   |      |Celery |
  | (DB)  |      | Cache |                            |Vector |      |Worker |
  +-------+      +-------+                            +-------+      +-------+
```

### 4.1 Golang 核心业务服务 (以 Gin 为例)
核心服务不处理复杂的 AI 推理，专注于极致的 I/O 读写。通过原生的 `goroutine` 调度，实现高并发无阻塞。

```go
package main

import (
	"context"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/go-redis/redis/v8"
)

var rdb *redis.Client
var ctx = context.Background()

func main() {
	// 初始化 Redis 连接
	rdb = redis.NewClient(&redis.Options{
		Addr: "localhost:6379",
	})

	r := gin.Default()

	// 核心业务：高并发记录进度
	r.POST("/api/v1/course/progress", func(c *gin.Context) {
		var req struct {
			UserID   string `json:"user_id"`
			CourseID string `json:"course_id"`
			Progress int    `json:"progress"`
		}
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return nil
		}

		// 异步写入缓存并回写 MySQL，极速响应客户端请求
		go func(uid, cid string, prog int) {
			// 1. 更新 Redis 缓存
			rdb.HSet(ctx, "user:"+uid+":progress", cid, prog)
			// 2. 达到阈值或定时批量刷入 MySQL
			saveProgressToDB(uid, cid, prog)
		}(req.UserID, req.CourseID, req.Progress)

		c.JSON(http.StatusOK, gin.H{"status": "recorded"})
	})

	r.Run(":8080")
}

func saveProgressToDB(userID, courseID string, progress int) {
	// 实际场景中，此处采用通道 (Channel) 缓冲，通过连接池批量写入数据库
	time.Sleep(50 * time.Millisecond) // 模拟持久化时延
}
```

---

## 五、 AI 伴学微服务 (FastAPI + AI 编排框架)

AI 伴学服务不直接与复杂的账务、支付数据库发生事务关联，而是通过统一的数据中台、JWT 凭证以及向量搜索引擎获取课程上下文，进而使用 RAG 技术和大模型进行高质量伴学。

### 5.1 FastAPI 异步 SSE 接口实现
FastAPI 原生支持 `StreamingResponse`。通过调用 LangChain 的异步流式发生器，能够将模型生成的 Token 实时发送给前端。

```python
# app/main.py
import asyncio
from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import jwt

app = FastAPI(title="ZhiXueTang-AI-Service")
JWT_SECRET = "ZhiHu-ZhiXueTang-Secret-Key"

class ChatRequest(BaseModel):
    prompt: string
    course_id: str

def verify_token(authorization: str = Header(...)):
    try:
        token = authorization.split(" ")[1]
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid Credentials")

async def fake_llm_stream_generator(prompt: str, course_context: str):
    # 此处模拟大模型与 RAG 检索返回的流
    full_response = f"[结合课程上下文: {course_context}] 针对您提问的 '{prompt}'，以下是知学堂 AI 助手的解答：
1. 重点知识回顾...
2. 推荐学习路径..."
    for word in full_response.split(" "):
        yield f"data: {word} 

"
        await asyncio.sleep(0.08) # 模拟流式生成延迟

@app.post("/api/v1/ai/assistant/chat")
async def chat_assistant(req: ChatRequest, user: dict = Depends(verify_token)):
    # 1. 模拟从 ES 向量数据库中检索 course_id 的关联课程文档 (RAG)
    course_context = "知学堂 Vue3 项目实战：响应式系统源码剖析"
    
    # 2. 启动异步发生器流式输出
    return StreamingResponse(
        fake_llm_stream_generator(req.prompt, course_context),
        media_type="text/event-stream"
    )
```

### 5.2 AGI 编排框架集成方案 (LlamaIndex + LangGraph + LangChain)
为了实现可追溯、支持图状态流转的“AI 伴学”，将知识检索与对话逻辑划分为两个引擎：

#### LlamaIndex (RAG 与知识库索引构建)
```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.vector_stores.elasticsearch import ElasticsearchStore

def initialize_course_index(course_id: str, document_dir: str):
    # 1. 加载本地课程 PDF 文档/视频字幕
    documents = SimpleDirectoryReader(document_dir).load_data()
    
    # 2. 构建 Elasticsearch 向量存储存储库
    vector_store = ElasticsearchStore(
        index_name=f"course_{course_id}_index",
        es_url="http://localhost:9200"
    )
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    # 3. 索引构建并持久化
    index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)
    return index
```

#### LangGraph (构建多轮智能决策流)
对于学员的复杂提问，需要判断是“常规闲聊”、“课程内容答疑（需要 RAG 检索）”还是“写代码调试”。使用 LangGraph 进行状态流转：

```
                    +------------------+
                    |  State: Message  |
                    +--------+---------+
                             |
                             v
                    +------------------+
                    |  Router Node     |
                    +---+--------+-----+
                        |        |
         [If Course Query]       [If Code Debug]
                        v        v
          +---------------+    +---------------+
          |  RAG Engine   |    | Code Sandbox  |
          |  (LlamaIndex) |    |  Executor     |
          +-------+-------+    +-------+-------+
                  |                    |
                  +--------+-----------+
                           |
                           v
                    +------+-----------+
                    |  LLM Synthesizer |
                    +------------------+
```

---

## 六、 异步任务、队列与高并发优化 (Celery + WS + 并发细节)

### 6.1 离线处理队列 (Celery)
教育场景中，学员提交作业批改、视频上传自动切片、PDF 转向量等，都属于 CPU / I/O 双重密集型长耗时任务，必须使用 Celery 异步队列，避免阻塞 FastAPI 线程。

```python
# tasks.py (Celery Worker)
from celery import Celery
import time

celery_app = Celery('tasks', broker='redis://localhost:6379/1', backend='redis://localhost:6379/2')

@celery_app.task
def process_uploaded_lecture_pdf(file_path: str, course_id: str):
    print(f"Starting OCR and chunking process for {file_path}")
    # 1. 模拟抽取 PDF 文本
    time.sleep(10) 
    # 2. 模拟切片并调用本地 Embedding 模型 (如 Text-Embedding-3-Large)
    # 3. 将向量数据持久化保存至 Elasticsearch
    print(f"Successfully vectorized course {course_id}")
    return {"status": "success", "chunks_created": 150}
```

### 6.2 WebSocket 实时课堂交互
直播互动、实时弹幕、学员状态实时提醒使用 Websocket。
1. **多端协同**：Go API 负责向特定房间广播消息。
2. **连接保活**：引入 Ping-Pong 心跳机制，客户端 30 秒无响应则断开，防止无效连接挤占连接池。

### 6.3 数据库模型与存储优化 (MySQL + Redis + ES)
*   **MySQL（核心表设计）**：
    *   `zhixue_users` (uid, username, pwd_hash, status)
    *   `zhixue_courses` (cid, title, teacher_id, status)
    *   `zhixue_orders` (oid, uid, cid, amount, pay_status, created_at) — 建立 `(uid, cid)` 复合索引加快权益校验。
*   **Redis（缓存与防刷）**：
    *   `user:{uid}:course:{cid}:lock` 设置分布式锁（PX 3000ms）防止高并发下重复提交购课订单或重复扣减知学币。
*   **Elasticsearch（检索分流）**：
    *   在 ES 层面完成检索的分流。课程基本信息的常规搜索、相似词模糊推荐在常规 ES 分片中进行；向量数据、大段知识库语料检索走专门的 K-NN (K-Nearest Neighbors) 相似度引擎分区，从而兼顾搜索性能。

---

## 七、 总结
本套开发方案将 Vue 3 的高效流式交互、Golang 的高并发极速吞吐、FastAPI 对 AGI 编排框架（LangChain / LangGraph / LlamaIndex）的友好生态和异步机制有机融合。在大批量重型数据（如音视频和长文档解析）的处理上，采用 Celery 进行削峰填谷，最终依托 MySQL、Redis、Elasticsearch 组成的三层持久化缓存数据链路，确保知学堂在新职人职业教育场景中具备弹性、高可用与高响应速度的技术核心竞争力。