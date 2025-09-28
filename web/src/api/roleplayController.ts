import type { 
  RoleplayIntentRequest, 
  RoleplayIntentResponse,
  RoleplayStreamRequest,
  RoleChatStreamRequest,
  SSEEvent
} from './types/roleplayTypes'

// 角色扮演意图检测接口
export const detectRoleplayIntent = async (data: RoleplayIntentRequest): Promise<RoleplayIntentResponse> => {
  const response = await fetch('http://localhost:9100/v1/intent/roleplay', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  })

  if (!response.ok) {
    throw new Error(`角色扮演检测失败: ${response.status}`)
  }

  return await response.json()
}

// 角色扮演流式自我介绍接口
export const startRoleplayStream = async (
  data: RoleplayStreamRequest,
  onEvent: (event: SSEEvent) => void
): Promise<void> => {
  console.log('🚀 调用角色扮演流式接口:', {
    url: 'http://localhost:9103/v1/roleplay/stream',
    data: data
  })

  const response = await fetch('http://localhost:9103/v1/roleplay/stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'text/event-stream'
    },
    body: JSON.stringify(data)
  })

  console.log('📡 接口响应状态:', response.status, response.statusText)

  if (!response.ok) {
    const errorText = await response.text()
    console.error('❌ 接口错误响应:', errorText)
    throw new Error(`角色扮演流式接口失败: ${response.status} - ${errorText}`)
  }

  const reader = response.body?.getReader()
  if (!reader) {
    throw new Error('无法获取响应流')
  }

  console.log('📖 开始读取 SSE 流...')
  const decoder = new TextDecoder()
  let buffer = ''

  try {
    while (true) {
      const { value, done } = await reader.read()
      if (done) {
        console.log('📖 SSE 流读取完成')
        break
      }

      buffer += decoder.decode(value, { stream: true })

      // 按 SSE 事件块分割
      const parts = buffer.split('\n\n')
      buffer = parts.pop()!

      for (const chunk of parts) {
        // 解析 event 与 data
        const lines = chunk.split('\n')
        let event = 'message'
        let data = ''
        
        for (const line of lines) {
          if (line.startsWith('event:')) {
            event = line.slice(6).trim()
          } else if (line.startsWith('data:')) {
            data += line.slice(5).trim()
          }
        }

        if (data) {
          try {
            // 解析完整的JSON数据
            const parsedData = JSON.parse(data)
            const eventData: SSEEvent = {
              event: parsedData.event || event,
              ...parsedData
            }
            console.log('📨 收到 SSE 事件:', eventData.event, eventData)
            onEvent(eventData)
          } catch (error) {
            console.error('❌ 解析 SSE 事件失败:', error, '原始数据:', data)
            onEvent({
              event: 'warn',
              error: '解析事件数据失败'
            })
          }
        }
      }
    }
  } catch (error) {
    console.error('角色扮演流式接口错误:', error)
    onEvent({
      event: 'warn',
      error: error instanceof Error ? error.message : '未知错误'
    })
  }
}

// 角色对话流式接口
export const startRoleChatStream = async (
  data: RoleChatStreamRequest,
  onEvent: (event: SSEEvent) => void
): Promise<void> => {
  const response = await fetch('http://localhost:9101/v1/rolechat/stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'text/event-stream'
    },
    body: JSON.stringify(data)
  })

  if (!response.ok) {
    throw new Error(`角色对话流式接口失败: ${response.status}`)
  }

  const reader = response.body?.getReader()
  if (!reader) {
    throw new Error('无法获取响应流')
  }

  const decoder = new TextDecoder()
  let buffer = ''

  try {
    while (true) {
      const { value, done } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })

      // 按 SSE 事件块分割
      const parts = buffer.split('\n\n')
      buffer = parts.pop()!

      for (const chunk of parts) {
        // 解析 event 与 data
        const lines = chunk.split('\n')
        let event = 'message'
        let data = ''
        
        for (const line of lines) {
          if (line.startsWith('event:')) {
            event = line.slice(6).trim()
          } else if (line.startsWith('data:')) {
            data += line.slice(5).trim()
          }
        }

        if (data) {
          try {
            // 解析完整的JSON数据
            const parsedData = JSON.parse(data)
            const eventData: SSEEvent = {
              event: parsedData.event || event,
              ...parsedData
            }
            onEvent(eventData)
          } catch (error) {
            console.error('解析 SSE 事件失败:', error)
            onEvent({
              event: 'warn',
              error: '解析事件数据失败'
            })
          }
        }
      }
    }
  } catch (error) {
    console.error('角色对话流式接口错误:', error)
    onEvent({
      event: 'warn',
      error: error instanceof Error ? error.message : '未知错误'
    })
  }
}
