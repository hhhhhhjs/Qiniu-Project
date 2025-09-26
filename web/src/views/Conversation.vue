<template>
  <div class="conversation-container">
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

    <!-- 麦克风控制按钮 -->
    <div class="mic-controls">
      <button
        v-if="!isRecording"
        @click="startMicrophone"
        class="mic-btn start"
        :disabled="!!audioError"
      >
        🎤 启用麦克风
      </button>
      <button
        v-else
        @click="stopMicrophone"
        class="mic-btn stop"
      >
        🔇 关闭麦克风
      </button>
      <div v-if="audioError" class="error-message">{{ audioError }}</div>
    </div>

    <div class="actions">
      <button class="hangup-btn" @click="handleHangup">挂断</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import VoiceWave3D from '@/components/VoiceWave3D.vue'
import { useAudioManager } from '@/composables/useAudioManager'

const route = useRoute()
const router = useRouter()

const robotRoleName = computed(() => (route.query.robotRoleName as string) || 'AI 助手')

// 音频管理器
const {
  isRecording,
  audioData,
  error: audioError,
  startRecording,
  stopRecording,
  getVolumeLevel,
  getFrequencies,
  isVoiceActive
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
}

// 监听音频数据变化
watch(audioData, (newData) => {
  if (newData) {
    isUserSpeaking.value = newData.isActive
    waveIntensity.value = Math.max(0.3, newData.volume * 2)
    audioFrequencies.value = newData.frequencies
  }
}, { deep: true })

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
  stopMicrophone() // 确保清理麦克风资源
})

function handleHangup() {
  stopMicrophone()
  router.back()
}
</script>

<style scoped>
.conversation-container {
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 50%, #cbd5e1 100%);
  color: #1e293b;
  width: 100%;
  height: 100vh;
  overflow: hidden;
}

.avatar-area {
  position: relative;
  margin-top: 12vh;
  width: 11rem;
  height: 11rem;
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
  position: absolute; bottom: -2.2rem; left: 50%; transform: translateX(-50%);
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
  position: absolute;
  bottom: 140px;
  left: 50%;
  transform: translateX(-50%);
  width: 85%;
  max-width: 600px;
  height: 120px;
  z-index: 1;
  backdrop-filter: blur(10px);
  border-radius: 16px;
}

.actions {
  position: absolute;
  bottom: 40px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
}
.hangup-btn {
  width: 74px; height: 74px; border-radius: 50%; border: none; cursor: pointer;
  color: #fff;
  background: linear-gradient(135deg, #ef4444, #dc2626);
  box-shadow: 0 8px 25px rgba(239, 68, 68, 0.3);
  transition: all 0.2s ease;
  border: 2px solid rgba(255, 255, 255, 0.2);
}
.hangup-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 35px rgba(239, 68, 68, 0.4);
}
.hangup-btn:active { transform: translateY(0); filter: brightness(.95); }

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
  .avatar-area { width: 9.5rem; height: 9.5rem; margin-top: 10vh; }
  .voice-wave-container {
    bottom: 100px;
    width: 95%;
    height: 160px;
    background: rgba(255, 255, 255, 0.8);
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