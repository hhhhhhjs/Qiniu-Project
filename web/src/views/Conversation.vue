<template>
  <div class="conversation-container">
    <!-- 上半部分：语音对话区域 -->
    <div class="voice-section">
      <div class="avatar-area">
        <div class="voice-avatar" :class="{ speaking: isAISpeaking }">
          <div v-if="avatarUrl" class="avatar-img" :style="{ backgroundImage: `url(${avatarUrl})` }" />
          <div v-else class="avatar-placeholder">{{ roleInitials }}</div>
        </div>
        <div v-for="i in 3" :key="i" :class="`ripple-${i}`" />
        <div class="role-name">{{ robotRoleName }}</div>
      </div>

      <div class="voice-wave-container">
        <VoiceWave3D
          :is-active="isUserSpeaking || isAISpeaking"
          :intensity="waveIntensity"
          :color="isUserSpeaking ? '#3b82f6' : '#8b5cf6'"
          :frequencies="audioFrequencies"
          :use-real-audio="useRealAudio"
        />
      </div>

      <!-- 状态指示器 -->
      <div class="status-indicator">
        <div v-if="!isConversationReady" class="status-item connecting">
          <div class="status-dot"></div>
          <span>正在连接语音服务...</span>
        </div>
        <div v-else-if="conversationState === 'listening'" class="status-item listening">
          <div class="status-dot"></div>
          <span>正在监听...</span>
        </div>
        <div v-else-if="conversationState === 'processing'" class="status-item processing">
          <div class="status-dot"></div>
          <span>正在处理...</span>
        </div>
        <div v-else-if="conversationState === 'speaking'" class="status-item speaking">
          <div class="status-dot"></div>
          <span>AI 正在回复...</span>
        </div>
        <div v-else-if="errorMessage" class="status-item error">
          <div class="status-dot"></div>
          <span>{{ errorMessage }}</span>
        </div>
        <div v-else class="status-item idle">
          <div class="status-dot"></div>
          <span>点击麦克风开始对话</span>
        </div>
      </div>
    </div>

    <!-- 下半部分：聊天面板 -->
    <div class="chat-section">
      <VoiceChatPanel
        ref="chatPanelRef"
        :is-listening="isRecording"
        :current-transcript="currentTranscript"
        :is-processing="isProcessingMessage"
        @send-message="handleSendMessage"
        @toggle-voice="handleToggleVoice"
      />
    </div>


  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import VoiceWave3D from '@/components/VoiceWave3D.vue'
import VoiceChatPanel from '@/components/VoiceChatPanel.vue'
import {
  createVoiceConversationManager,
  checkVoiceSupport,
  getRecommendedAudioConfig,
  type VoiceConversationManager,
  type VoiceConversationConfig
} from '@/api/voiceConversation'
import { ElMessage } from 'element-plus'

const route = useRoute()

const robotRoleName = computed(() => (route.query.robotRoleName as string) || 'AI 助手')

// 语音对话管理器
let voiceManager: VoiceConversationManager | null = null

// 角色头像映射
import jixiaomeiImg from '@/assets/images/roles/jixiaomei.jpg'
import petAssistant from '@/assets/images/roles/petAssistant.jpg'
import healthAssistant from '@/assets/images/roles/healthAssistant.jpg'

const roleImages: Record<string, string> = {
  '集小美': jixiaomeiImg,
  '猫狗宠物助手': petAssistant,
  '养生助手': healthAssistant,
}

const avatarUrl = computed(() => roleImages[robotRoleName.value] || '')
const roleInitials = computed(() => robotRoleName.value?.slice(0, 1) || '机')

// 语音状态
const isUserSpeaking = ref(false)
const isAISpeaking = ref(false)
const waveIntensity = ref(0.5)
const useRealAudio = ref(true) // 使用真实音频
const audioFrequencies = ref<number[]>([])

// 聊天相关状态
const currentTranscript = ref('')
const isProcessingMessage = ref(false)
const chatPanelRef = ref<InstanceType<typeof VoiceChatPanel>>()
const isRecording = ref(false)

// 语音对话状态
const conversationState = ref<'idle' | 'listening' | 'processing' | 'speaking'>('idle')
const isConversationReady = ref(false)
const errorMessage = ref('')

// 初始化语音对话管理器
async function initializeVoiceConversation() {
  try {
    // 检查浏览器支持
    const support = checkVoiceSupport()
    if (!support.webRTC || !support.speechSynthesis || !support.webSocket) {
      throw new Error('浏览器不支持所需的语音功能')
    }

    // 获取推荐配置
    const audioConfig = getRecommendedAudioConfig()

    // 创建配置
    const config: VoiceConversationConfig = {
      ragEndpoint: 'http://localhost:8000/v1/workflow/stream',
      asrEndpoint: 'ws://localhost:10095',
      sampleRate: audioConfig.sampleRate,
      chunkSize: audioConfig.chunkSize,
      hotwords: {
        '阿里巴巴': 20,
        '通义实验室': 30,
        [robotRoleName.value]: 25
      }
    }

    // 创建语音对话管理器
    voiceManager = createVoiceConversationManager(config)

    // 设置事件回调
    voiceManager.setCallbacks({
      onTranscript: (text, isFinal) => {
        currentTranscript.value = text
        if (isFinal && text.trim()) {
          // 最终识别结果会自动发送到 RAG 工作流
          console.log('Final transcript:', text)
        }
      },

      onResponse: (text) => {
        // 机器人回复
        chatPanelRef.value?.addAIMessage(text)
        console.log('Bot response:', text)
      },

      onError: (error) => {
        console.error('Voice conversation error:', error)
        errorMessage.value = handleVoiceError(error)
        ElMessage.error(errorMessage.value)
      },

      onStateChange: (state) => {
        conversationState.value = state
        updateUIState(state)
      }
    })

    // 启动对话会话
    await voiceManager.startConversation()
    isConversationReady.value = true
    errorMessage.value = ''

    console.log('Voice conversation initialized successfully')
  } catch (error) {
    console.error('Failed to initialize voice conversation:', error)
    errorMessage.value = error instanceof Error ? error.message : '初始化语音对话失败'
    ElMessage.error(errorMessage.value)
  }
}

// 处理语音错误
function handleVoiceError(error: Error): string {
  if (error.message.includes('WebSocket')) {
    return '语音识别服务连接失败，请检查网络连接'
  } else if (error.message.includes('getUserMedia')) {
    return '无法访问麦克风，请检查浏览器权限设置'
  } else if (error.message.includes('HTTP error')) {
    return 'RAG 服务连接失败，请检查服务器状态'
  } else {
    return `语音对话出现错误: ${error.message}`
  }
}

// 更新 UI 状态
function updateUIState(state: 'idle' | 'listening' | 'processing' | 'speaking') {
  switch (state) {
    case 'listening':
      isRecording.value = true
      isUserSpeaking.value = true
      isAISpeaking.value = false
      isProcessingMessage.value = false
      waveIntensity.value = 0.7
      break
    case 'processing':
      isRecording.value = false
      isUserSpeaking.value = false
      isAISpeaking.value = false
      isProcessingMessage.value = true
      waveIntensity.value = 0.3
      currentTranscript.value = '' // 清空实时转录
      break
    case 'speaking':
      isRecording.value = false
      isUserSpeaking.value = false
      isAISpeaking.value = true
      isProcessingMessage.value = false
      waveIntensity.value = 0.8
      break
    case 'idle':
    default:
      isRecording.value = false
      isUserSpeaking.value = false
      isAISpeaking.value = false
      isProcessingMessage.value = false
      waveIntensity.value = 0.3
      break
  }
}

// 聊天相关方法
const handleSendMessage = async (content: string) => {
  if (!voiceManager || !isConversationReady.value) {
    ElMessage.warning('语音对话未准备就绪，请稍后再试')
    return
  }

  // 这里可以直接调用 RAG 工作流
  // 由于我们的语音对话管理器已经集成了 RAG，这里可以复用相同的逻辑
  try {
    isProcessingMessage.value = true

    // 模拟调用 RAG 工作流（实际应该调用相同的接口）
    // 这里为了演示，我们直接模拟一个回复
    setTimeout(() => {
      const aiResponse = `收到你的消息："${content}"，我正在为你查找相关信息...`
      chatPanelRef.value?.addAIMessage(aiResponse)
      isProcessingMessage.value = false
    }, 1000)
  } catch (error) {
    console.error('发送消息失败:', error)
    isProcessingMessage.value = false
    ElMessage.error('发送消息失败')
  }
}

const handleToggleVoice = async () => {
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

// 生命周期钩子
onMounted(async () => {
  // 初始化语音对话
  await initializeVoiceConversation()

  // 模拟音频频谱数据（用于视觉效果）
  const updateAudioFrequencies = () => {
    if (isUserSpeaking.value || isAISpeaking.value) {
      // 生成模拟的音频频谱数据
      const frequencies = Array.from({ length: 32 }, () => Math.random() * 255)
      audioFrequencies.value = frequencies
    } else {
      audioFrequencies.value = []
    }
  }

  // 定期更新音频频谱（用于视觉效果）
  const timer = setInterval(updateAudioFrequencies, 100)

  // 清理函数
  onUnmounted(() => {
    clearInterval(timer)
    cleanupVoiceConversation()
  })
})


</script>

<style scoped>
.conversation-container {
  position: relative;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 50%, #cbd5e1 100%);
  color: #1e293b;
  width: 100%;
  height: 100vh;
  overflow: hidden;
}

/* 上半部分：语音对话区域 */
.voice-section {
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 45vh;
  flex-shrink: 0;
}

/* 下半部分：聊天面板 */
.chat-section {
  position: relative;
  height: 50vh;
  margin: 0 20px 20px 20px;
  flex-shrink: 0;
}

.avatar-area {
  position: relative;
  margin-top: 8vh;
  width: 10rem;
  height: 10rem;
  display: flex;
  justify-content: center;
  align-items: center;
}
.voice-avatar {
  position: relative;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  overflow: hidden;
  box-shadow: 0 8px 30px rgba(59, 130, 246, 0.15);
  border: 3px solid rgba(59, 130, 246, 0.3);
  z-index: 2;
  transition: transform .2s ease;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
}
.voice-avatar.speaking { animation: pulse 1.1s ease-in-out infinite; }
.avatar-img { width: 100%; height: 100%; background-size: cover; background-position: center; }
.avatar-placeholder {
  width: 100%; height: 100%; display:flex; align-items:center; justify-content:center;
  font-size: 3rem;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  color: white;
  font-weight: bold;
}
.role-name {
  position: absolute; bottom: -1.5rem; left: 50%; transform: translateX(-50%);
  font-size: 0.95rem; color: #64748b; font-weight: 500;
  width: 200px;
  text-align: center;
}

/* 多层涟漪 */
.ripple-1, .ripple-2, .ripple-3 {
  position: absolute; inset: 0; border-radius: 50%; border: 2px solid rgba(59, 130, 246, 0.4);
  transform: scale(1); opacity: 0; pointer-events: none; z-index: 1;
}
.ripple-1 { animation: ripple 2.3s ease-out infinite; }
.ripple-2 { animation: ripple 2.3s ease-out .5s infinite; }
.ripple-3 { animation: ripple 2.3s ease-out 1s infinite; }

/* 3D 频谱容器 */
.voice-wave-container {
  position: relative;
  margin-top: 3vh;
  width: 85%;
  max-width: 600px;
  height: 100px;
  z-index: 1;
  backdrop-filter: blur(10px);
  border-radius: 16px;
}

/* 状态指示器 */
.status-indicator {
  position: absolute;
  bottom: 2vh;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(15px);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  transition: all 0.3s ease;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  animation: pulse-dot 2s infinite;
}

.status-item.connecting .status-dot {
  background: #f59e0b;
}

.status-item.listening .status-dot {
  background: #10b981;
}

.status-item.processing .status-dot {
  background: #3b82f6;
}

.status-item.speaking .status-dot {
  background: #8b5cf6;
}

.status-item.error .status-dot {
  background: #ef4444;
}

.status-item.idle .status-dot {
  background: #6b7280;
}

@keyframes pulse-dot {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.5;
    transform: scale(1.2);
  }
}



@keyframes pulse { 0%{transform:scale(1)} 40%{transform:scale(1.03)} 70%{transform:scale(1)} 100%{transform:scale(1)} }
@keyframes ripple { 0%{opacity:0; transform:scale(1)} 30%{opacity:.8} 100%{opacity:0; transform:scale(1.4)} }

/* 麦克风控制 */
.mic-controls {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 10;
  display: flex;
  flex-direction: column;
  gap: 10px;
  align-items: flex-end;
}

.mic-btn {
  padding: 10px 18px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 24px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(15px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.mic-btn.start {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  border-color: rgba(16, 185, 129, 0.3);
}

.mic-btn.start:hover {
  background: linear-gradient(135deg, #059669, #047857);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.3);
}

.mic-btn.stop {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white;
  border-color: rgba(239, 68, 68, 0.3);
}

.mic-btn.stop:hover {
  background: linear-gradient(135deg, #dc2626, #b91c1c);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(239, 68, 68, 0.3);
}

.mic-btn:disabled {
  background: rgba(148, 163, 184, 0.6);
  color: rgba(255, 255, 255, 0.7);
  cursor: not-allowed;
  transform: none;
  border-color: rgba(148, 163, 184, 0.3);
}

.error-message {
  color: #ef4444;
  font-size: 12px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  padding: 6px 12px;
  border-radius: 8px;
  border: 1px solid rgba(239, 68, 68, 0.2);
  max-width: 200px;
  text-align: right;
  box-shadow: 0 2px 8px rgba(239, 68, 68, 0.1);
}

@media (max-width: 640px) {
  .voice-section {
    height: 50vh;
  }

  .chat-section {
    height: 45vh;
    margin: 0 10px 10px 10px;
  }

  .avatar-area {
    width: 8rem;
    height: 8rem;
    margin-top: 6vh;
  }

  .voice-wave-container {
    width: 95%;
    height: 80px;
    margin-top: 2vh;
  }

  .mic-controls {
    top: 10px;
    right: 10px;
  }

  .mic-btn {
    font-size: 12px;
    padding: 8px 14px;
  }


}
</style>