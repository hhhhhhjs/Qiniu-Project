import { ref, onUnmounted } from 'vue'

export interface AudioData {
  volume: number
  frequencies: number[]
  isActive: boolean
}

export function useAudioManager() {
  const isRecording = ref(false)
  const audioData = ref<AudioData>({
    volume: 0,
    frequencies: [],
    isActive: false
  })
  const error = ref<string>('')

  let mediaStream: MediaStream | null = null
  let audioContext: AudioContext | null = null
  let analyser: AnalyserNode | null = null
  let microphone: MediaStreamAudioSourceNode | null = null
  let animationId: number | null = null
  let dataArray: Uint8Array | null = null

  // 启动麦克风录音
  async function startRecording() {
    try {
      error.value = ''
      
      // 请求麦克风权限
      mediaStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          sampleRate: 44100
        }
      })

      // 创建音频上下文
      audioContext = new (window.AudioContext || (window as any).webkitAudioContext)()
      
      // 创建分析器节点
      analyser = audioContext.createAnalyser()
      analyser.fftSize = 256 // 频谱分析的精度
      analyser.smoothingTimeConstant = 0.8 // 平滑处理
      
      // 连接麦克风到分析器
      microphone = audioContext.createMediaStreamSource(mediaStream)
      microphone.connect(analyser)
      
      // 创建数据数组
      const bufferLength = analyser.frequencyBinCount
      dataArray = new Uint8Array(bufferLength)
      
      isRecording.value = true
      
      // 开始分析音频
      analyzeAudio()
      
      console.log('麦克风录音已启动')
      
    } catch (err) {
      console.error('启动麦克风失败:', err)
      error.value = err instanceof Error ? err.message : '无法访问麦克风'
    }
  }

  // 停止录音
  function stopRecording() {
    if (animationId) {
      cancelAnimationFrame(animationId)
      animationId = null
    }

    if (mediaStream) {
      mediaStream.getTracks().forEach(track => track.stop())
      mediaStream = null
    }

    if (audioContext) {
      audioContext.close()
      audioContext = null
    }

    microphone = null
    analyser = null
    dataArray = null
    
    isRecording.value = false
    audioData.value = {
      volume: 0,
      frequencies: [],
      isActive: false
    }
    
    console.log('麦克风录音已停止')
  }

  // 分析音频数据
  function analyzeAudio() {
    if (!analyser || !dataArray) return

    animationId = requestAnimationFrame(analyzeAudio)

    // 获取频域数据
    analyser.getByteFrequencyData(dataArray)
    
    // 计算音量 (RMS)
    let sum = 0
    for (let i = 0; i < dataArray.length; i++) {
      sum += dataArray[i] * dataArray[i]
    }
    const rms = Math.sqrt(sum / dataArray.length)
    const volume = rms / 255 // 归一化到 0-1
    
    // 提取频谱数据 (取前60个频率段用于可视化)
    const frequencies = Array.from(dataArray.slice(0, 60)).map(value => value / 255)
    
    // 检测是否有声音活动 (音量阈值)
    const isActive = volume > 0.01
    
    audioData.value = {
      volume,
      frequencies,
      isActive
    }
  }

  // 获取音量级别 (0-1)
  function getVolumeLevel(): number {
    return audioData.value.volume
  }

  // 获取频谱数据
  function getFrequencies(): number[] {
    return audioData.value.frequencies
  }

  // 检查是否有语音活动
  function isVoiceActive(): boolean {
    return audioData.value.isActive
  }

  // 清理资源
  onUnmounted(() => {
    stopRecording()
  })

  return {
    isRecording,
    audioData,
    error,
    startRecording,
    stopRecording,
    getVolumeLevel,
    getFrequencies,
    isVoiceActive
  }
}
