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
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import VoiceWave3D from '@/components/VoiceWave3D.vue'
import VoiceChatPanel from '@/components/VoiceChatPanel.vue'
import { useAudioManager } from '@/composables/useAudioManager'

const route = useRoute()

const robotRoleName = computed(() => (route.query.robotRoleName as string) || 'AI 助手')

// 音频管理器
const {
  isRecording,
  audioData,
  startRecording,
  stopRecording,
} = useAudioManager()

// 角色头像映射
import jixiaomeiImg from '@/assets/images/roles/jixiaomei.jpg'
import feiduduImg from '@/assets/images/roles/肥嘟嘟左卫门.jpg'
import labixxImg from '@/assets/images/roles/image.png'

const roleImages: Record<string, string> = {
  '集小美': jixiaomeiImg,
  '肥嘟嘟': feiduduImg,
  '蜡笔小新': labixxImg,
}

const avatarUrl = computed(() => roleImages[robotRoleName.value] || '')
const roleInitials = computed(() => robotRoleName.value?.slice(0, 1) || '机')

// 语音状态
const isUserSpeaking = ref(false)
const isAISpeaking = ref(false)
const waveIntensity = ref(0.5)
const useRealAudio = ref(false)
const audioFrequencies = ref<number[]>([])

// 聊天相关状态
const currentTranscript = ref('')
const isProcessingMessage = ref(false)
const chatPanelRef = ref<InstanceType<typeof VoiceChatPanel>>()

// 语音转文字相关状态
let transcriptionTimer: number | null = null
let lastTranscriptTime = 0
const transcriptionDelay = 1000 // 1秒延迟发送消息

// 麦克风控制方法
async function startMicrophone() {
  try {
    await startRecording()
    useRealAudio.value = true
  } catch (err) {
    console.error('启动麦克风失败:', err)
  }
}

function stopMicrophone() {
  stopRecording()
  useRealAudio.value = false
  audioFrequencies.value = []
  currentTranscript.value = ''

  // 清理转录定时器
  if (transcriptionTimer) {
    clearTimeout(transcriptionTimer)
    transcriptionTimer = null
  }
}

// 聊天相关方法
const handleSendMessage = async (content: string) => {
  isProcessingMessage.value = true

  try {
    // 这里可以调用 AI API 获取回复
    // 模拟 AI 回复
    setTimeout(() => {
      const aiResponse = `收到你的消息："${content}"，我正在思考如何回复...`
      chatPanelRef.value?.addAIMessage(aiResponse)
      isProcessingMessage.value = false

      // 模拟 AI 语音回复
      isAISpeaking.value = true
      setTimeout(() => {
        isAISpeaking.value = false
      }, 3000)
    }, 1000)
  } catch (error) {
    console.error('发送消息失败:', error)
    isProcessingMessage.value = false
  }
}

const handleToggleVoice = () => {
  if (isRecording.value) {
    stopMicrophone()
  } else {
    startMicrophone()
  }
}

// 监听音频数据变化
watch(audioData, (newData) => {
  if (newData) {
    isUserSpeaking.value = newData.isActive
    waveIntensity.value = Math.max(0.3, newData.volume * 2)
    audioFrequencies.value = newData.frequencies

    // 处理语音转文字
    handleVoiceTranscription(newData.isActive)
  }
}, { deep: true })

// 处理语音转文字逻辑
const handleVoiceTranscription = (isActive: boolean) => {
  if (isActive && isRecording.value) {
    // 用户正在说话，更新实时转录
    if (Date.now() - lastTranscriptTime > 500) { // 500ms 更新一次
      simulateVoiceTranscription()
      lastTranscriptTime = Date.now()
    }

    // 清除之前的定时器
    if (transcriptionTimer) {
      clearTimeout(transcriptionTimer)
    }
  } else if (!isActive && currentTranscript.value.trim()) {
    // 用户停止说话，延迟发送消息
    if (transcriptionTimer) {
      clearTimeout(transcriptionTimer)
    }

    transcriptionTimer = window.setTimeout(() => {
      if (currentTranscript.value.trim()) {
        handleSendMessage(currentTranscript.value.trim())
        currentTranscript.value = ''
      }
    }, transcriptionDelay)
  }
}

// 模拟语音转文字
const simulateVoiceTranscription = () => {
  const sampleTexts = [
    '你好',
    '你好，我想',
    '你好，我想问一下',
    '你好，我想问一下关于',
    '你好，我想问一下关于天气的',
    '你好，我想问一下关于天气的情况'
  ]

  const randomIndex = Math.floor(Math.random() * sampleTexts.length)
  currentTranscript.value = sampleTexts[randomIndex]
}

let timer: number | null = null
onMounted(() => {

  // AI 说话状态模拟（可以根据实际 AI 回答状态来控制）
  timer = window.setInterval(() => {
    // 如果没有使用真实音频，则模拟 AI 说话
    if (!useRealAudio.value) {
      // 随机模拟 AI 说话状态
      if (Math.random() < 0.1) {
        isAISpeaking.value = !isAISpeaking.value
      }

      if (isAISpeaking.value) {
        waveIntensity.value = 0.4 + Math.random() * 0.4
      }
    }
  }, 500)
})

onUnmounted(() => {
  if (timer) window.clearInterval(timer)
  if (transcriptionTimer) clearTimeout(transcriptionTimer)
  stopMicrophone() // 确保清理麦克风资源
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