import { ref } from 'vue'

export function useTTS() {
  const isAISpeaking = ref(false)

  // TTS 播放函数
  async function playTTSResponse(
    text: string,
    onStateChange?: (state: 'idle' | 'listening' | 'processing' | 'speaking') => void
  ): Promise<void> {
    try {
      console.log('🔊 开始TTS文字转语音播放:', text.substring(0, 50) + '...')
      onStateChange?.('speaking')
      isAISpeaking.value = true

      // 尝试调用本地 TTS 服务
      const ttsResponse = await fetch('http://127.0.0.1:8080/v1/tts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          text: text,
          voice: 'zh-CN-XiaoxiaoNeural', // 可以根据角色调整语音
          rate: 1.0,
          pitch: 1.0
        })
      })

      if (ttsResponse.ok) {
        const audioBlob = await ttsResponse.blob()
        const audioUrl = URL.createObjectURL(audioBlob)
        const audio = new Audio(audioUrl)

        audio.onended = () => {
          onStateChange?.('idle')
          isAISpeaking.value = false
          URL.revokeObjectURL(audioUrl)
        }

        audio.onerror = () => {
          console.warn('TTS 音频播放失败，回退到浏览器 TTS')
          fallbackToBrowserTTS(text, onStateChange)
        }

        await audio.play()
      } else {
        throw new Error(`TTS 服务响应错误: ${ttsResponse.status}`)
      }
    } catch (error) {
      console.warn('TTS 服务调用失败，回退到浏览器 TTS:', error)
      fallbackToBrowserTTS(text, onStateChange)
    }
  }

  // 回退到浏览器 TTS
  function fallbackToBrowserTTS(
    text: string,
    onStateChange?: (state: 'idle' | 'listening' | 'processing' | 'speaking') => void
  ): void {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text)

      utterance.onend = () => {
        onStateChange?.('idle')
        isAISpeaking.value = false
      }

      utterance.onerror = () => {
        onStateChange?.('idle')
        isAISpeaking.value = false
      }

      // 设置中文语音
      const voices = speechSynthesis.getVoices()
      const chineseVoice = voices.find(voice => voice.lang.includes('zh'))
      if (chineseVoice) {
        utterance.voice = chineseVoice
      }

      speechSynthesis.speak(utterance)
    } else {
      // 如果浏览器不支持 TTS，使用定时器模拟
      const estimatedDuration = text.length * 100 // 估算播放时间
      setTimeout(() => {
        onStateChange?.('idle')
        isAISpeaking.value = false
      }, estimatedDuration)
    }
  }

  // 停止 TTS 播放
  function stopTTS() {
    if ('speechSynthesis' in window) {
      speechSynthesis.cancel()
    }
    isAISpeaking.value = false
  }

  return {
    // 状态
    isAISpeaking,
    
    // 方法
    playTTSResponse,
    fallbackToBrowserTTS,
    stopTTS
  }
}
