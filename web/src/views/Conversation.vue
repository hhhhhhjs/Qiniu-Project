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

      <!-- 调试信息 (开发环境) -->
      <div v-if="true" class="debug-info" style="position: absolute; top: 10px; right: 10px; background: rgba(0,0,0,0.7); color: white; padding: 8px; border-radius: 4px; font-size: 12px; z-index: 1000;">
        <div>模式: {{ isRoleplayMode ? '角色扮演' : '普通对话' }}</div>
        <div>系统状态: {{ isSystemReady ? '已准备' : '初始化中' }}</div>
        <div v-if="isRoleplayMode">原始输入: {{ originalInput }}</div>
        <div v-if="isRoleplayMode">角色数据: {{ roleplayData ? '已加载' : '未加载' }}</div>
        <div v-if="isRoleplayMode">介绍完成: {{ isIntroductionComplete ? '是' : '否' }}</div>
        <div v-if="isRoleplayMode">角色准备: {{ isRoleplayReady ? '是' : '否' }}</div>
        <div v-if="!isRoleplayMode">语音连接中: {{ isVoiceConnecting ? '是' : '否' }}</div>
        <div v-if="!isRoleplayMode">语音准备: {{ isConversationReady ? '是' : '否' }}</div>
      </div>

      <!-- 状态指示器 -->
      <div class="status-indicator">
        <div v-if="isRoleplayMode && !isSystemReady" class="status-item connecting">
          <div class="status-dot"></div>
          <span>正在初始化角色...</span>
        </div>
        <div v-else-if="!isRoleplayMode && isVoiceConnecting" class="status-item connecting">
          <div class="status-dot"></div>
          <span>语音服务连接中...</span>
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
          <span>{{ isRoleplayMode ? '开始对话吧' : '可以开始对话' }}</span>
        </div>
      </div>


    </div>

    <!-- 下半部分：聊天面板 -->
    <div class="chat-section">
      <VoiceChatPanel
        ref="chatPanelRef"
        :current-transcript="currentTranscript"
        :is-processing="isProcessingMessage"
        :is-listening="conversationState === 'listening'"
        @send-message="handleSendMessage"
        @toggle-voice="handleToggleVoice"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { getUserMes } from '@/api/userController'
import VoiceWave3D from '@/components/VoiceWave3D.vue'
import VoiceChatPanel from '@/components/VoiceChatPanel.vue'

// 使用新的 composables
import { useVoiceConversation } from '@/composables/useVoiceConversation'
import { useRoleplay } from '@/composables/useRoleplay'
import { useChatHandler } from '@/composables/useChatHandler'
import { useTTS } from '@/composables/useTTS'

// 角色头像映射
import jixiaomeiImg from '@/assets/images/roles/jixiaomei.jpg'
import petAssistant from '@/assets/images/roles/petAssistant.jpg'
import healthAssistant from '@/assets/images/roles/healthAssistant.jpg'

const route = useRoute()
const robotRoleName = computed(() => (route.query.robotRoleName as string) || 'AI 助手')

const roleImages: Record<string, string> = {
  '集小美': jixiaomeiImg,
  '猫狗宠物助手': petAssistant,
  '养生助手': healthAssistant,
}

const avatarUrl = computed(() => roleImages[robotRoleName.value] || '')
const roleInitials = computed(() => robotRoleName.value?.slice(0, 1) || '机')

// 使用 composables
const voiceConversation = useVoiceConversation()
const roleplay = useRoleplay()
const chatHandler = useChatHandler()
const tts = useTTS()

// 从 composables 中解构状态和方法
const {
  isConversationReady,
  conversationState,
  errorMessage,
  currentTranscript,
  isVoiceConnecting,
  initializeVoiceConversation,
  toggleVoice,
  cleanupVoiceConversation
} = voiceConversation

const {
  isRoleplayMode,
  originalInput,
  roleplayData,
  isIntroductionComplete,
  isRoleplayReady,
  initializeRoleplay,
  handleRoleplayChat
} = roleplay

const {
  isProcessingMessage,
  handleSendMessage: handleSendMessageBase
} = chatHandler

const {
  isAISpeaking,
  playTTSResponse
} = tts

// 本地状态
const isUserSpeaking = ref(false)
const waveIntensity = ref(0.5)
const useRealAudio = ref(true)
const audioFrequencies = ref<number[]>([])
const chatPanelRef = ref<InstanceType<typeof VoiceChatPanel>>()

// 计算整体准备状态
const isSystemReady = computed(() => {
  if (isRoleplayMode.value) {
    // 角色扮演模式：需要角色初始化完成
    return isRoleplayReady.value
  } else {
    // 普通模式：文字对话立即可用，语音对话可选
    return true // 普通模式下立即可用
  }
})

// 更新 UI 状态
function updateUIState(state: 'idle' | 'listening' | 'processing' | 'speaking') {
  switch (state) {
    case 'listening':
      isUserSpeaking.value = true
      waveIntensity.value = 0.8
      break
    case 'processing':
      isUserSpeaking.value = false
      waveIntensity.value = 0.6
      break
    case 'speaking':
      isUserSpeaking.value = false
      waveIntensity.value = 0.4
      break
    case 'idle':
    default:
      isUserSpeaking.value = false
      waveIntensity.value = 0.3
      break
  }
}



// 语音切换处理
const handleToggleVoice = async () => {
  console.log('🎤 用户点击麦克风按钮，当前状态:', conversationState.value)
  await toggleVoice()
}

// 消息发送处理
const handleSendMessage = async (content: string) => {
  await handleSendMessageBase(
    content,
    isRoleplayMode.value,
    roleplayData.value,
    isIntroductionComplete.value,
    isConversationReady.value,
    () => chatPanelRef.value?.startStreamingAIMessage(),
    (messageId: string, text: string) => chatPanelRef.value?.updateStreamingMessage(messageId, text),
    (messageId: string) => chatPanelRef.value?.finishStreamingMessage(messageId),
    (text: string) => playTTSResponse(text, updateUIState),
    async (content: string, messageId: string) => {
      await handleRoleplayChat(
        content,
        messageId,
        (messageId: string, text: string) => chatPanelRef.value?.updateStreamingMessage(messageId, text),
        (messageId: string) => chatPanelRef.value?.finishStreamingMessage(messageId),
        (text: string) => playTTSResponse(text, updateUIState)
      )
    }
  )
}

// 生命周期钩子
onMounted(async () => {
  // 检查是否是合法用户（不阻塞后续初始化）
  try {
    await getUserMes()
  } catch (error) {
    console.warn('用户认证失败，但功能仍可正常使用:', error)
  }

  // 检查URL参数，确保角色扮演模式的条件
  console.log('URL参数检查:', {
    isRoleplay: route.query.isRoleplay,
    originalInput: route.query.originalInput,
    robotRoleName: route.query.robotRoleName
  })

  // 只有在非角色扮演模式下才初始化语音对话（后台进行，不阻塞文字对话）
  if (!isRoleplayMode.value) {
    // 异步初始化语音对话，不等待完成
    initializeVoiceConversation(
      robotRoleName.value,
      (text: string, isFinal: boolean) => {
        if (isFinal && text.trim()) {
          console.log('🎤 10095语音转文字完成:', text)
          // 清除实时转录显示
          currentTranscript.value = ''

          // 先创建用户消息气泡
          const userMessageId = chatPanelRef.value?.addUserMessage(text.trim())
          console.log('👤 语音用户消息已创建:', userMessageId)

          // 然后调用后端接口
          handleSendMessage(text.trim())
        }
      },
      undefined,
      updateUIState
    ).catch(error => {
      console.warn('语音对话初始化失败，但文字对话仍可使用:', error)
    })
  }

  // 如果是角色扮演模式，进行角色初始化
  if (isRoleplayMode.value && originalInput.value) {
    await initializeRoleplay(
      (messageId: string, text: string) => chatPanelRef.value?.updateStreamingMessage(messageId, text),
      (messageId: string) => chatPanelRef.value?.finishStreamingMessage(messageId),
      () => chatPanelRef.value?.startStreamingAIMessage(),
      (text: string) => playTTSResponse(text, updateUIState)
    )
    // 角色初始化完成后，再启动语音对话
    await initializeVoiceConversation(
      robotRoleName.value,
      (text: string, isFinal: boolean) => {
        if (isFinal && text.trim()) {
          console.log('🎤 10095语音转文字完成:', text)
          // 清除实时转录显示
          currentTranscript.value = ''

          // 先创建用户消息气泡
          const userMessageId = chatPanelRef.value?.addUserMessage(text.trim())
          console.log('👤 语音用户消息已创建:', userMessageId)

          // 然后调用后端接口
          handleSendMessage(text.trim())
        }
      },
      undefined,
      updateUIState
    )
  }

  // 模拟音频频谱数据（用于视觉效果）
  const updateAudioFrequencies = () => {
    if (isUserSpeaking.value || isAISpeaking.value) {
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


}
</style>
