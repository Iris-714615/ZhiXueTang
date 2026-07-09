// AI 服务，负责与 FastAPI 后端的 AI 接口交互
const AI_SERVICE_BASE = 'http://localhost:8001'  // FastAPI AI 服务地址

/**
 * 流式请求 AI 助手对话
 * 使用 fetch + ReadableStream 实现 SSE（Server-Sent Events）
 * @param prompt 用户输入的提示词
 * @param courseId 当前课程 ID
 * @param onChunk 每收到一段文本时的回调
 * @param onComplete 流式响应完成时的回调
 * @param onError 发生错误时的回调
 */
export async function fetchAIAssistantStream(
  prompt: string,
  courseId: string,
  onChunk: (text: string) => void,
  onComplete: () => void,
  onError?: (error: any) => void
) {
  try {
    // 从 localStorage 获取用户 token
    const token = localStorage.getItem('token') || ''

    // 发起 POST 请求，携带 Authorization 头与请求体
    const response = await fetch(`${AI_SERVICE_BASE}/api/v1/ai/assistant/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ prompt, course_id: courseId })
    })

    if (!response.ok) {
      throw new Error(`请求失败，状态码：${response.status}`)
    }

    if (!response.body) {
      throw new Error('响应流不可用')
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let buffer = ''  // 用于缓存不完整的行

    // 循环读取流式数据
    while (true) {
      const { done, value } = await reader.read()
      if (done) {
        break
      }

      // 将二进制数据解码为文本并追加到缓冲区
      buffer += decoder.decode(value, { stream: true })

      // 按换行符分割，处理完整的行
      const lines = buffer.split('\n')
      // 最后一行可能不完整，保留到下一次处理
      buffer = lines.pop() || ''

      for (const line of lines) {
        const trimmed = line.trim()
        // 跳过空行
        if (!trimmed) continue
        // 只处理 data: 开头的行
        if (!trimmed.startsWith('data:')) continue

        // 去掉 "data:" 前缀及可能的空格
        const data = trimmed.slice(5).trim()
        // 收到结束标记，完成流式读取
        if (data === '[DONE]') {
          onComplete()
          return
        }

        try {
          // 尝试解析 JSON 数据，兼容 content / text / delta 字段
          const parsed = JSON.parse(data)
          const text = parsed.content || parsed.text || parsed.delta || ''
          if (text) {
            onChunk(text)
          }
        } catch {
          // 非 JSON 格式，直接作为文本传递
          if (data) {
            onChunk(data)
          }
        }
      }
    }

    // 处理缓冲区中剩余的数据
    const remaining = buffer.trim()
    if (remaining.startsWith('data:')) {
      const data = remaining.slice(5).trim()
      if (data && data !== '[DONE]') {
        try {
          const parsed = JSON.parse(data)
          const text = parsed.content || parsed.text || parsed.delta || ''
          if (text) {
            onChunk(text)
          }
        } catch {
          if (data) {
            onChunk(data)
          }
        }
      }
    }

    // 流读取完毕，触发完成回调
    onComplete()
  } catch (error) {
    if (onError) {
      onError(error)
    } else {
      console.error('AI 助手流式请求出错：', error)
    }
  }
}

/**
 * 构建课程知识库索引
 * @param courseId 课程 ID
 * @param documentDir 文档目录路径
 */
export async function buildCourseIndex(courseId: string, documentDir: string) {
  const token = localStorage.getItem('token') || ''
  const response = await fetch(`${AI_SERVICE_BASE}/api/v1/ai/knowledge/build_index`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ course_id: courseId, document_dir: documentDir })
  })

  if (!response.ok) {
    throw new Error(`构建索引失败，状态码：${response.status}`)
  }

  return await response.json()
}

/**
 * 检索课程知识库
 * @param query 查询文本
 * @param courseId 课程 ID
 * @param topK 返回的最相关结果数量，默认 5
 */
export async function searchKnowledge(query: string, courseId: string, topK: number = 5) {
  const token = localStorage.getItem('token') || ''
  const response = await fetch(`${AI_SERVICE_BASE}/api/v1/ai/knowledge/search`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ query, course_id: courseId, top_k: topK })
  })

  if (!response.ok) {
    throw new Error(`知识检索失败，状态码：${response.status}`)
  }

  return await response.json()
}
