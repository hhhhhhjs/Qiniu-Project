import { ref } from 'vue'
import { ElMessage } from 'element-plus'

export function useChatHandler() {
  const isProcessingMessage = ref(false)

  // 普通聊天处理函数
  async function handleNormalChat(
    content: string,
    messageId: string,
    onStreamingMessage?: (messageId: string, text: string) => void,
    onFinishMessage?: (messageId: string) => void,
    onPlayTTS?: (text: string) => void
  ): Promise<void> {
    const ragEndpoint = 'http://localhost:9004/v1/workflow/stream'
    let fullResponse = ''

    console.log('🚀 调用9004机器人对话接口:', {
      endpoint: ragEndpoint,
      content: content,
      messageId: messageId
    })

    const response = await fetch(ragEndpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream'
      },
      body: JSON.stringify({ text: content })
    })

    console.log('📡 普通对话接口响应状态:', response.status, response.statusText)

    if (!response.ok) {
      const errorText = await response.text()
      console.error('❌ 普通对话接口错误:', errorText)
      throw new Error(`RAG 工作流请求失败: ${response.status} - ${errorText}`)
    }

    const reader = response.body?.getReader()
    if (!reader) {
      throw new Error('无法读取响应流')
    }

    console.log('📖 开始读取普通对话流...')

    const decoder = new TextDecoder()

    try {
      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value, { stream: true })
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              
              if (data.event === 'delta' && data.text) {
                fullResponse += data.text
                onStreamingMessage?.(messageId, fullResponse)
              } else if (data.event === 'done') {
                console.log('RAG 工作流完成')
              }
            } catch (error) {
              console.warn('解析 RAG 响应失败:', error)
            }
          }
        }
      }
    } finally {
      reader.releaseLock()
    }

    onFinishMessage?.(messageId)

    // 播放 TTS 语音
    if (fullResponse.trim()) {
      console.log('🔊 调用TTS文字转语音:', fullResponse.substring(0, 50) + '...')
      onPlayTTS?.(fullResponse)
    }
  }

  // 主要的消息发送处理函数
  async function handleSendMessage(
    content: string,
    isRoleplayMode: boolean,
    roleplayData: any,
    isIntroductionComplete: boolean,
    isConversationReady: boolean,
    onStartMessage?: () => string | undefined,
    onStreamingMessage?: (messageId: string, text: string) => void,
    onFinishMessage?: (messageId: string) => void,
    onPlayTTS?: (text: string) => void,
    onRoleplayChat?: (content: string, messageId: string) => Promise<void>
  ) {
    // 角色扮演模式需要等待角色初始化完成
    if (isRoleplayMode && !isIntroductionComplete) {
      ElMessage.warning('角色正在初始化中，请稍后再试')
      return
    }

    // 普通模式下，文字对话立即可用，不需要等待语音服务
    // 只有在角色扮演模式下才需要检查系统准备状态
    if (isRoleplayMode && !isConversationReady) {
      ElMessage.warning('对话系统未准备就绪，请稍后再试')
      return
    }

    console.log('发送消息:', {
      content,
      isRoleplayMode,
      hasRoleplayData: !!roleplayData,
      isIntroductionComplete
    })

    try {
      isProcessingMessage.value = true

      // 开始流式 AI 消息
      const messageId = onStartMessage?.()
      if (!messageId) {
        throw new Error('无法创建消息')
      }

      // 判断是否为角色扮演模式
      if (isRoleplayMode && roleplayData && isIntroductionComplete) {
        // 第三步：角色对话流式接口
        console.log('使用角色对话接口')
        await onRoleplayChat?.(content, messageId)
      } else if (!isRoleplayMode) {
        // 普通 RAG 工作流
        console.log('使用普通对话接口')
        await handleNormalChat(content, messageId, onStreamingMessage, onFinishMessage, onPlayTTS)
      } else {
        throw new Error('角色扮演模式配置不完整')
      }
    } catch (error) {
      console.error('发送消息失败:', error)
      ElMessage.error('发送消息失败，请稍后重试')
    } finally {
      isProcessingMessage.value = false
    }
  }

  return {
    // 状态
    isProcessingMessage,
    
    // 方法
    handleSendMessage,
    handleNormalChat
  }
}
