/**
 * 语音对话相关接口
 * 包含语音识别、RAG工作流、语音合成等功能
 */

// 事件类型定义
export interface WorkflowEvent {
  event: 'start' | 'normalize' | 'recall' | 'rerank' | 'delta' | 'done' | 'error'
  ts?: string
  elapsed_ms?: number
  text?: string
  hit_count?: number
  skipped?: boolean
  candidates?: number
  preview?: string
  reason?: string
  answer?: string
  timings?: any
  total_ms?: number
  stage?: string
  message?: string
}

// FunASR WebSocket 消息类型
export interface FunASRMessage {
  mode: 'offline' | '2pass' | 'online'
  wav_name: string
  wav_format?: string
  is_speaking: boolean
  hotwords?: string
  itn?: boolean
  audio_fs?: number
  chunk_size?: number[]
  svs_lang?: string
  svs_itn?: boolean
}

// FunASR 识别结果
export interface FunASRResult {
  mode: string
  wav_name: string
  text: string
  is_final: boolean
  timestamp?: string
  stamp_sents?: any[]
}

// 语音对话配置
export interface VoiceConversationConfig {
  // RAG 工作流配置
  ragEndpoint?: string
  // FunASR WebSocket 配置
  asrEndpoint?: string
  // TTS 配置
  ttsEndpoint?: string
  // 音频配置
  sampleRate?: number
  chunkSize?: number[]
  // 热词配置
  hotwords?: Record<string, number>
}

/**
 * RAG 工作流流式接口调用
 * @param text 用户输入的文本
 * @param onEvent 事件回调函数
 * @param config 配置选项
 */
export async function callRAGWorkflowStream(
  text: string,
  onEvent: (event: WorkflowEvent) => void,
  config: VoiceConversationConfig = {}
): Promise<void> {
  const endpoint = config.ragEndpoint || 'http://localhost:9004/v1/workflow/stream'

  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream'
      },
      body: JSON.stringify({ text })
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const reader = response.body?.getReader()
    if (!reader) {
      throw new Error('Failed to get response reader')
    }

    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { value, done } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })

      let idx
      while ((idx = buffer.indexOf('\n\n')) !== -1) {
        const chunk = buffer.slice(0, idx)
        buffer = buffer.slice(idx + 2)

        chunk.split('\n').forEach(line => {
          if (line.startsWith('data:')) {
            const jsonStr = line.slice(5).trim()
            if (!jsonStr) return

            try {
              const event: WorkflowEvent = JSON.parse(jsonStr)
              onEvent(event)
            } catch (error) {
              console.error('Failed to parse SSE event:', error, jsonStr)
            }
          }
        })
      }
    }
  } catch (error) {
    console.error('RAG workflow stream error:', error)
    onEvent({
      event: 'error',
      message: error instanceof Error ? error.message : 'Unknown error'
    })
  }
}

/**
 * FunASR WebSocket 语音识别类
 */
export class FunASRWebSocket {
  private ws: WebSocket | null = null
  private config: VoiceConversationConfig
  private onResult: (result: FunASRResult) => void
  private onError: (error: Error) => void

  constructor(
    config: VoiceConversationConfig,
    onResult: (result: FunASRResult) => void,
    onError: (error: Error) => void
  ) {
    this.config = config
    this.onResult = onResult
    this.onError = onError
  }

  /**
   * 连接 WebSocket
   */
  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      const endpoint = this.config.asrEndpoint || 'ws://localhost:10095'

      try {
        this.ws = new WebSocket(endpoint)

        this.ws.onopen = () => {
          console.log('FunASR WebSocket connected')
          resolve()
        }

        this.ws.onmessage = (event) => {
          try {
            const result: FunASRResult = JSON.parse(event.data)
            this.onResult(result)
          } catch (error) {
            console.error('Failed to parse ASR result:', error)
            this.onError(new Error('Failed to parse ASR result'))
          }
        }

        this.ws.onerror = (error) => {
          console.error('FunASR WebSocket error:', error)
          this.onError(new Error('WebSocket connection error'))
          reject(error)
        }

        this.ws.onclose = () => {
          console.log('FunASR WebSocket disconnected')
          this.ws = null
        }
      } catch (error) {
        reject(error)
      }
    })
  }

  /**
   * 开始识别会话
   * @param mode 识别模式
   * @param wavName 音频文件名
   */
  startRecognition(mode: 'offline' | '2pass' | 'online' = '2pass', wavName: string = 'audio'): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      throw new Error('WebSocket is not connected')
    }

    const hotwordsStr = this.config.hotwords
      ? JSON.stringify(this.config.hotwords)
      : '{"阿里巴巴":20,"通义实验室":30}'

    const message: FunASRMessage = {
      mode,
      wav_name: wavName,
      wav_format: 'pcm',
      is_speaking: true,
      chunk_size: this.config.chunkSize || [5, 10, 5],
      hotwords: hotwordsStr,
      itn: true,
      audio_fs: this.config.sampleRate || 16000,
      svs_lang: 'auto',
      svs_itn: true
    }

    this.ws.send(JSON.stringify(message))
  }

  /**
   * 发送音频数据
   * @param audioData PCM 音频数据
   */
  sendAudioData(audioData: ArrayBuffer): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      throw new Error('WebSocket is not connected')
    }

    this.ws.send(audioData)
  }

  /**
   * 结束识别
   */
  endRecognition(): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      throw new Error('WebSocket is not connected')
    }

    const endMessage = { is_speaking: false }
    this.ws.send(JSON.stringify(endMessage))
  }

  /**
   * 断开连接
   */
  disconnect(): void {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  /**
   * 获取连接状态
   */
  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN
  }
}

/**
 * 音频录制管理类
 */
export class AudioRecorder {
  private audioContext: AudioContext | null = null
  private source: MediaStreamAudioSourceNode | null = null
  private workletNode: AudioWorkletNode | null = null
  private stream: MediaStream | null = null
  private isRecording = false
  private onAudioData: (audioData: ArrayBuffer) => void

  constructor(onAudioData: (audioData: ArrayBuffer) => void) {
    this.onAudioData = onAudioData
  }

  /**
   * 开始录音
   */
  async startRecording(sampleRate: number = 16000): Promise<void> {
    try {
      // 获取麦克风权限
      this.stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true
        }
      })

      // 创建音频上下文
      this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)({
        sampleRate
      })

      // 创建音频源
      this.source = this.audioContext.createMediaStreamSource(this.stream)

      // 使用 MediaRecorder 作为备选方案
      this.startMediaRecorderFallback()

      this.isRecording = true
      console.log('Audio recording started')
    } catch (error) {
      console.error('Failed to start recording:', error)
      throw error
    }
  }

  /**
   * 使用 MediaRecorder 作为备选方案
   */
  private startMediaRecorderFallback(): void {
    if (!this.stream) return

    const mediaRecorder = new MediaRecorder(this.stream, {
      mimeType: 'audio/webm;codecs=opus'
    })

    const audioChunks: Blob[] = []

    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunks.push(event.data)
      }
    }

    mediaRecorder.onstop = async () => {
      const audioBlob = new Blob(audioChunks, { type: 'audio/webm' })
      const arrayBuffer = await audioBlob.arrayBuffer()

      // 这里需要将 WebM 转换为 PCM，实际项目中可能需要使用 Web Audio API 或其他库
      // 暂时直接传递原始数据
      this.onAudioData(arrayBuffer)
    }

    // 每100ms收集一次数据
    mediaRecorder.start(100)

    // 定期停止并重新开始以获得实时数据
    const intervalId = setInterval(() => {
      if (!this.isRecording) {
        clearInterval(intervalId)
        return
      }

      if (mediaRecorder.state === 'recording') {
        mediaRecorder.stop()
        setTimeout(() => {
          if (this.isRecording && mediaRecorder.state === 'inactive') {
            audioChunks.length = 0 // 清空之前的数据
            mediaRecorder.start(100)
          }
        }, 10)
      }
    }, 100)
  }

  /**
   * 停止录音
   */
  stopRecording(): void {
    this.isRecording = false

    if (this.workletNode) {
      this.workletNode.disconnect()
      this.workletNode = null
    }

    if (this.source) {
      this.source.disconnect()
      this.source = null
    }

    if (this.audioContext) {
      this.audioContext.close()
      this.audioContext = null
    }

    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop())
      this.stream = null
    }

    console.log('Audio recording stopped')
  }

  /**
   * 获取录音状态
   */
  getRecordingState(): boolean {
    return this.isRecording
  }
}

/**
 * 语音合成管理类 - 支持本地 TTS 服务和浏览器原生 TTS
 */
export class TextToSpeech {
  private synth: SpeechSynthesis
  private currentUtterance: SpeechSynthesisUtterance | null = null
  private ttsEndpoint: string | undefined
  private currentAudio: HTMLAudioElement | null = null

  constructor(ttsEndpoint?: string) {
    this.synth = window.speechSynthesis
    this.ttsEndpoint = ttsEndpoint
  }

  /**
   * 播放文本
   * @param text 要播放的文本
   * @param options 播放选项
   */
  async speak(text: string, options: {
    voice?: SpeechSynthesisVoice
    rate?: number
    pitch?: number
    volume?: number
    onEnd?: () => void
    onError?: (error: any) => void
    useLocalTTS?: boolean
  } = {}): Promise<void> {
    // 停止当前播放
    this.stop()

    // 优先使用本地 TTS 服务
    if (this.ttsEndpoint && (options.useLocalTTS !== false)) {
      try {
        await this.speakWithLocalTTS(text, options)
        return
      } catch (error) {
        console.warn('Local TTS failed, falling back to browser TTS:', error)
        // 如果本地 TTS 失败，回退到浏览器 TTS
      }
    }

    // 使用浏览器原生 TTS
    this.speakWithBrowserTTS(text, options)
  }

  /**
   * 使用本地 TTS 服务播放
   */
  private async speakWithLocalTTS(text: string, options: {
    onEnd?: () => void
    onError?: (error: any) => void
  }): Promise<void> {
    if (!this.ttsEndpoint) {
      throw new Error('TTS endpoint not configured')
    }

    try {
      // 调用本地 TTS 服务
      const response = await fetch(`${this.ttsEndpoint}/tts`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          text,
          voice: 'default', // 可以根据需要配置
          speed: 1.0,
          pitch: 1.0
        })
      })

      if (!response.ok) {
        throw new Error(`TTS service error: ${response.status}`)
      }

      // 获取音频数据
      const audioBlob = await response.blob()
      const audioUrl = URL.createObjectURL(audioBlob)

      // 播放音频
      this.currentAudio = new Audio(audioUrl)

      this.currentAudio.onended = () => {
        URL.revokeObjectURL(audioUrl)
        this.currentAudio = null
        if (options.onEnd) options.onEnd()
      }

      this.currentAudio.onerror = (error) => {
        URL.revokeObjectURL(audioUrl)
        this.currentAudio = null
        if (options.onError) options.onError(error)
      }

      await this.currentAudio.play()
    } catch (error) {
      if (options.onError) options.onError(error)
      throw error
    }
  }

  /**
   * 使用浏览器原生 TTS 播放
   */
  private speakWithBrowserTTS(text: string, options: {
    voice?: SpeechSynthesisVoice
    rate?: number
    pitch?: number
    volume?: number
    onEnd?: () => void
    onError?: (error: any) => void
  }): void {
    this.currentUtterance = new SpeechSynthesisUtterance(text)

    // 设置参数
    if (options.voice) this.currentUtterance.voice = options.voice
    if (options.rate) this.currentUtterance.rate = options.rate
    if (options.pitch) this.currentUtterance.pitch = options.pitch
    if (options.volume) this.currentUtterance.volume = options.volume

    // 设置回调
    if (options.onEnd) {
      this.currentUtterance.onend = options.onEnd
    }
    if (options.onError) {
      this.currentUtterance.onerror = options.onError
    }

    // 开始播放
    this.synth.speak(this.currentUtterance)
  }

  /**
   * 停止播放
   */
  stop(): void {
    // 停止浏览器 TTS
    if (this.synth.speaking) {
      this.synth.cancel()
    }
    this.currentUtterance = null

    // 停止本地 TTS 音频
    if (this.currentAudio) {
      this.currentAudio.pause()
      this.currentAudio.currentTime = 0
      this.currentAudio = null
    }
  }

  /**
   * 暂停播放
   */
  pause(): void {
    if (this.synth.speaking) {
      this.synth.pause()
    }
  }

  /**
   * 恢复播放
   */
  resume(): void {
    if (this.synth.paused) {
      this.synth.resume()
    }
  }

  /**
   * 获取可用的语音列表
   */
  getVoices(): SpeechSynthesisVoice[] {
    return this.synth.getVoices()
  }

  /**
   * 获取播放状态
   */
  isSpeaking(): boolean {
    return this.synth.speaking || (this.currentAudio !== null && !this.currentAudio.paused)
  }
}

/**
 * 完整的语音对话管理类
 */
export class VoiceConversationManager {
  private config: VoiceConversationConfig
  private funASR: FunASRWebSocket | null = null
  private audioRecorder: AudioRecorder | null = null
  private tts: TextToSpeech
  private isConversationActive = false
  private currentSessionId: string = ''

  // 事件回调
  private onTranscript?: (text: string, isFinal: boolean) => void
  private onResponse?: (text: string) => void
  private onError?: (error: Error) => void
  private onStateChange?: (state: 'idle' | 'listening' | 'processing' | 'speaking') => void

  constructor(config: VoiceConversationConfig = {}) {
    this.config = {
      ragEndpoint: 'http://localhost:9004/v1/workflow/stream',
      asrEndpoint: 'ws://localhost:10095',
      ttsEndpoint: 'http://localhost:8080',
      sampleRate: 16000,
      chunkSize: [5, 10, 5],
      hotwords: { '阿里巴巴': 20, '通义实验室': 30 },
      ...config
    }

    this.tts = new TextToSpeech(this.config.ttsEndpoint)
  }

  /**
   * 设置事件回调
   */
  setCallbacks(callbacks: {
    onTranscript?: (text: string, isFinal: boolean) => void
    onResponse?: (text: string) => void
    onError?: (error: Error) => void
    onStateChange?: (state: 'idle' | 'listening' | 'processing' | 'speaking') => void
  }): void {
    this.onTranscript = callbacks.onTranscript
    this.onResponse = callbacks.onResponse
    this.onError = callbacks.onError
    this.onStateChange = callbacks.onStateChange
  }

  /**
   * 开始语音对话
   */
  async startConversation(): Promise<void> {
    if (this.isConversationActive) {
      throw new Error('Conversation is already active')
    }

    try {
      this.currentSessionId = this.generateSessionId()
      this.setState('idle')

      // 初始化 FunASR WebSocket
      this.funASR = new FunASRWebSocket(
        this.config,
        (result) => this.handleASRResult(result),
        (error) => this.handleError(error)
      )

      await this.funASR.connect()

      // 初始化音频录制
      this.audioRecorder = new AudioRecorder((audioData) => {
        if (this.funASR && this.funASR.isConnected()) {
          this.funASR.sendAudioData(audioData)
        }
      })

      this.isConversationActive = true
      console.log('Voice conversation started')
    } catch (error) {
      this.handleError(error instanceof Error ? error : new Error('Failed to start conversation'))
    }
  }

  /**
   * 开始监听
   */
  async startListening(): Promise<void> {
    if (!this.isConversationActive || !this.funASR || !this.audioRecorder) {
      throw new Error('Conversation is not active')
    }

    try {
      this.setState('listening')

      // 开始 ASR 识别
      this.funASR.startRecognition('2pass', `session_${this.currentSessionId}`)

      // 开始录音
      await this.audioRecorder.startRecording(this.config.sampleRate)

      console.log('Started listening')
    } catch (error) {
      this.handleError(error instanceof Error ? error : new Error('Failed to start listening'))
    }
  }

  /**
   * 停止监听
   */
  stopListening(): void {
    if (!this.isConversationActive) return

    try {
      this.setState('processing')

      if (this.audioRecorder) {
        this.audioRecorder.stopRecording()
      }

      if (this.funASR) {
        this.funASR.endRecognition()
      }

      console.log('Stopped listening')
    } catch (error) {
      this.handleError(error instanceof Error ? error : new Error('Failed to stop listening'))
    }
  }

  /**
   * 结束对话
   */
  stopConversation(): void {
    this.isConversationActive = false
    this.setState('idle')

    if (this.audioRecorder) {
      this.audioRecorder.stopRecording()
      this.audioRecorder = null
    }

    if (this.funASR) {
      this.funASR.disconnect()
      this.funASR = null
    }

    this.tts.stop()
    console.log('Voice conversation stopped')
  }

  /**
   * 处理 ASR 识别结果
   */
  private handleASRResult(result: FunASRResult): void {
    if (this.onTranscript) {
      this.onTranscript(result.text, result.is_final)
    }

    // 如果是最终结果，发送到 RAG 工作流
    if (result.is_final && result.text.trim()) {
      this.processUserInput(result.text)
    }
  }

  /**
   * 处理用户输入，调用 RAG 工作流
   */
  private async processUserInput(text: string): Promise<void> {
    this.setState('processing')

    let fullResponse = ''

    try {
      await callRAGWorkflowStream(text, (event) => {
        switch (event.event) {
          case 'delta':
            if (event.text) {
              fullResponse += event.text
            }
            break

          case 'done':
            if (event.answer) {
              fullResponse = event.answer
            }
            this.handleBotResponse(fullResponse)
            break

          case 'error':
            this.handleError(new Error(event.message || 'RAG workflow error'))
            break
        }
      }, this.config)
    } catch (error) {
      this.handleError(error instanceof Error ? error : new Error('Failed to process user input'))
    }
  }

  /**
   * 处理机器人回复
   */
  private handleBotResponse(text: string): void {
    if (this.onResponse) {
      this.onResponse(text)
    }

    // 播放语音回复
    this.setState('speaking')
    this.tts.speak(text, {
      onEnd: () => {
        this.setState('idle')
        // 可以选择自动开始下一轮监听
        // this.startListening()
      },
      onError: (error) => {
        this.handleError(new Error(`TTS error: ${error.error}`))
      }
    })
  }

  /**
   * 设置状态并触发回调
   */
  private setState(state: 'idle' | 'listening' | 'processing' | 'speaking'): void {
    if (this.onStateChange) {
      this.onStateChange(state)
    }
  }

  /**
   * 处理错误
   */
  private handleError(error: Error): void {
    console.error('Voice conversation error:', error)
    if (this.onError) {
      this.onError(error)
    }
    this.setState('idle')
  }

  /**
   * 生成会话 ID
   */
  private generateSessionId(): string {
    return Date.now().toString(36) + Math.random().toString(36).substring(2)
  }

  /**
   * 获取对话状态
   */
  isActive(): boolean {
    return this.isConversationActive
  }

  /**
   * 获取当前会话 ID
   */
  getSessionId(): string {
    return this.currentSessionId
  }
}

/**
 * 创建语音对话管理器的便捷函数
 */
export function createVoiceConversationManager(config?: VoiceConversationConfig): VoiceConversationManager {
  return new VoiceConversationManager(config)
}

/**
 * 检查浏览器是否支持语音功能
 */
export function checkVoiceSupport(): {
  webRTC: boolean // 是否支持音视频传输
  speechSynthesis: boolean // 语音朗读
  webSocket: boolean // 是否支持 ws
} {
  return {
    webRTC: !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia),
    speechSynthesis: 'speechSynthesis' in window,
    webSocket: 'WebSocket' in window
  }
}

/**
 * 获取推荐的音频配置
 */
export function getRecommendedAudioConfig(): {
  sampleRate: number
  chunkSize: number[]
  constraints: MediaStreamConstraints
  
} {
  return {
    sampleRate: 16000,
    chunkSize: [5, 10, 5],
    constraints: {
      audio: {
        sampleRate: 16000,
        channelCount: 1,
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true
      }
    }
  }
}

// 默认导出主要的管理类
export default VoiceConversationManager