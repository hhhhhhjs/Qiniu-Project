import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  createVoiceConversationManager,
  checkVoiceSupport,
  getRecommendedAudioConfig,
  type VoiceConversationManager,
  type VoiceConversationConfig
} from '@/api/voiceConversation'
import { checkAllServices, formatServiceReport } from '@/utils/serviceHealthCheck'

export function useVoiceConversation() {
  // 状态管理
  const isConversationReady = ref(false)
  const conversationState = ref<'idle' | 'listening' | 'processing' | 'speaking'>('idle')
  const errorMessage = ref('')
  const currentTranscript = ref('')
  const isVoiceConnecting = ref(false) // 真实的语音连接状态
  
  // 语音对话管理器
  let voiceManager: VoiceConversationManager | null = null

  // 初始化语音对话管理器
  async function initializeVoiceConversation(
    robotRoleName: string,
    onTranscript?: (text: string, isFinal: boolean) => void,
    onError?: (error: Error) => void,
    onStateChange?: (state: 'idle' | 'listening' | 'processing' | 'speaking') => void
  ) {
    try {
      isVoiceConnecting.value = true
      console.log('🔄 开始初始化语音对话服务...')
      // 检查浏览器支持
      const support = checkVoiceSupport()
      if (!support.webRTC || !support.speechSynthesis || !support.webSocket) {
        throw new Error('浏览器不支持所需的语音功能')
      }

      // 检查服务状态
      console.log('🔍 正在检查服务状态...')
      const services = await checkAllServices()
      const report = formatServiceReport(services)
      console.log(report)

      // 检查关键服务是否在线
      const offlineServices = services.filter(s => s.status === 'offline')
      if (offlineServices.length > 0) {
        const offlineNames = offlineServices.map(s => s.name).join(', ')
        console.warn(`以下服务离线: ${offlineNames}，将使用模拟模式进行开发调试`)
        // 开发模式下不显示警告，避免干扰调试
        // ElMessage.warning(`以下服务离线: ${offlineNames}，部分功能可能无法正常使用`)
      }

      // 获取推荐配置
      const audioConfig = getRecommendedAudioConfig()

      // 创建配置
      const config: VoiceConversationConfig = {
        ragEndpoint: 'http://localhost:9004/v1/workflow/stream',
        asrEndpoint: 'ws://localhost:10195',
        ttsEndpoint: 'http://127.0.0.1:8080/v1/tts',
        sampleRate: audioConfig.sampleRate,
        chunkSize: audioConfig.chunkSize,
        hotwords: {
          '阿里巴巴': 20,
          '通义实验室': 30,
          [robotRoleName]: 25
        }
      }

      // 创建语音对话管理器
      voiceManager = createVoiceConversationManager(config)

      // 设置事件回调
      voiceManager.setCallbacks({
        onTranscript: (text, isFinal) => {
          currentTranscript.value = text
          if (onTranscript) {
            onTranscript(text, isFinal)
          }
        },

        onResponse: (text) => {
          // 这个回调在新的架构中不再使用，因为响应通过 handleSendMessage 处理
          console.log('Bot response (deprecated):', text)
        },

        onError: (error) => {
          console.error('Voice conversation error:', error)
          errorMessage.value = handleVoiceError(error)
          ElMessage.error(errorMessage.value)
          if (onError) {
            onError(error)
          }
        },

        onStateChange: (state) => {
          conversationState.value = state
          updateUIState(state)
          if (onStateChange) {
            onStateChange(state)
          }
        }
      })

      // 启动对话会话
      await voiceManager.startConversation()
      isConversationReady.value = true
      isVoiceConnecting.value = false
      errorMessage.value = ''

      console.log('✅ 语音对话初始化成功')
    } catch (error) {
      console.error('❌ 语音对话初始化失败:', error)
      isConversationReady.value = false
      isVoiceConnecting.value = false
      errorMessage.value = error instanceof Error ? error.message : '初始化语音对话失败'
      // 不显示错误消息，因为语音功能是可选的
      console.warn('语音功能不可用，但文字对话仍可正常使用')
    }
  }

  // 处理语音错误
  function handleVoiceError(error: Error): string {
    if (error.message.includes('WebSocket')) {
      return '语音识别服务连接失败，请检查网络连接'
    } else if (error.message.includes('getUserMedia')) {
      return '无法访问麦克风，请检查浏览器权限设置'
    } else if (error.message.includes('HTTP error')) {
      return '语音服务请求失败，请检查服务状态'
    } else {
      return `语音对话出现错误: ${error.message}`
    }
  }

  // 更新 UI 状态
  function updateUIState(state: 'idle' | 'listening' | 'processing' | 'speaking') {
    // 这个函数的具体实现需要在组件中处理，因为涉及到组件的响应式状态
    console.log('Voice state changed:', state)
  }

  // 切换语音状态
  async function toggleVoice() {
    if (!voiceManager || !isConversationReady.value) {
      ElMessage.warning('语音对话未准备就绪')
      return
    }

    try {
      if (conversationState.value === 'listening') {
        // 停止监听
        voiceManager.stopListening()
      } else if (conversationState.value === 'idle') {
        // 开始监听
        await voiceManager.startListening()
      }
    } catch (error) {
      console.error('切换语音状态失败:', error)
      ElMessage.error('语音操作失败')
    }
  }

  // 清理语音对话
  function cleanupVoiceConversation() {
    if (voiceManager) {
      voiceManager.stopConversation()
      voiceManager = null
    }
    isConversationReady.value = false
    conversationState.value = 'idle'
    currentTranscript.value = ''
    errorMessage.value = ''
  }

  return {
    // 状态
    isConversationReady,
    conversationState,
    errorMessage,
    currentTranscript,
    isVoiceConnecting,

    // 方法
    initializeVoiceConversation,
    toggleVoice,
    cleanupVoiceConversation,

    // 内部方法（可选暴露）
    handleVoiceError,
    updateUIState
  }
}
